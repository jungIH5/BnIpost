package com.bnipost.service;

import com.bnipost.entity.User;
import com.bnipost.repository.UserRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;

import java.util.Map;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class NaverOAuthService {

    @Value("${naver.client-id}")
    private String clientId;

    @Value("${naver.client-secret}")
    private String clientSecret;

    @Value("${naver.redirect-uri}")
    private String redirectUri;

    @Value("${naver.auth-url}")
    private String authUrl;

    @Value("${naver.token-url}")
    private String tokenUrl;

    @Value("${naver.profile-url}")
    private String profileUrl;

    private final UserRepository userRepository;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    public String buildAuthorizationUrl(String state) {
        return authUrl
                + "?response_type=code"
                + "&client_id=" + clientId
                + "&redirect_uri=" + redirectUri
                + "&state=" + state;
    }

    public User processCallback(String code, String state) {
        String accessToken = exchangeCodeForToken(code, state);
        JsonNode profile = fetchNaverProfile(accessToken);

        JsonNode response = profile.get("response");
        String providerId = response.get("id").asText();
        String email = response.has("email") ? response.get("email").asText() : providerId + "@naver.com";
        String nickname = response.has("nickname") ? response.get("nickname").asText() : "네이버 사용자";
        String profileImage = response.has("profile_image") ? response.get("profile_image").asText() : null;

        return userRepository.findByProviderAndProviderId(User.Provider.NAVER, providerId)
                .map(user -> {
                    user.setNaverAccessToken(accessToken);
                    user.setNickname(nickname);
                    user.setProfileImage(profileImage);
                    return userRepository.save(user);
                })
                .orElseGet(() -> userRepository.save(User.builder()
                        .email(email)
                        .nickname(nickname)
                        .profileImage(profileImage)
                        .provider(User.Provider.NAVER)
                        .providerId(providerId)
                        .naverAccessToken(accessToken)
                        .build()));
    }

    private String exchangeCodeForToken(String code, String state) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);

        MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
        params.add("grant_type", "authorization_code");
        params.add("client_id", clientId);
        params.add("client_secret", clientSecret);
        params.add("code", code);
        params.add("state", state);

        HttpEntity<MultiValueMap<String, String>> request = new HttpEntity<>(params, headers);
        ResponseEntity<Map> response = restTemplate.postForEntity(tokenUrl, request, Map.class);

        if (!response.getStatusCode().is2xxSuccessful() || response.getBody() == null) {
            throw new RuntimeException("Naver token exchange failed");
        }
        return (String) response.getBody().get("access_token");
    }

    private JsonNode fetchNaverProfile(String accessToken) {
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(accessToken);
        HttpEntity<Void> entity = new HttpEntity<>(headers);

        ResponseEntity<String> response = restTemplate.exchange(profileUrl, HttpMethod.GET, entity, String.class);
        try {
            return objectMapper.readTree(response.getBody());
        } catch (Exception e) {
            throw new RuntimeException("Failed to parse Naver profile", e);
        }
    }

    public String generateState() {
        return UUID.randomUUID().toString();
    }
}
