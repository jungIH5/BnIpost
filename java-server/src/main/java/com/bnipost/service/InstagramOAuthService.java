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

@Slf4j
@Service
@RequiredArgsConstructor
public class InstagramOAuthService {

    @Value("${instagram.client-id}")
    private String clientId;

    @Value("${instagram.client-secret}")
    private String clientSecret;

    @Value("${instagram.redirect-uri}")
    private String redirectUri;

    @Value("${instagram.auth-url}")
    private String authUrl;

    @Value("${instagram.token-url}")
    private String tokenUrl;

    @Value("${instagram.long-lived-token-url}")
    private String longLivedTokenUrl;

    @Value("${instagram.profile-url}")
    private String profileUrl;

    private final UserRepository userRepository;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    public String buildAuthorizationUrl() {
        return authUrl
                + "?client_id=" + clientId
                + "&redirect_uri=" + redirectUri
                + "&scope=instagram_business_basic,instagram_business_content_publish"
                + "&response_type=code";
    }

    public User processCallback(String code) {
        String shortToken = exchangeCodeForToken(code);
        String longToken = exchangeForLongLivedToken(shortToken);
        JsonNode profile = fetchInstagramProfile(longToken);

        String instagramUserId = profile.get("id").asText();
        String username = profile.has("username") ? profile.get("username").asText() : "instagram_user";
        String email = instagramUserId + "@instagram.local";

        return userRepository.findByProviderAndProviderId(User.Provider.INSTAGRAM, instagramUserId)
                .map(user -> {
                    user.setInstagramAccessToken(longToken);
                    user.setInstagramUserId(instagramUserId);
                    user.setNickname(username);
                    return userRepository.save(user);
                })
                .orElseGet(() -> userRepository.save(User.builder()
                        .email(email)
                        .nickname(username)
                        .provider(User.Provider.INSTAGRAM)
                        .providerId(instagramUserId)
                        .instagramAccessToken(longToken)
                        .instagramUserId(instagramUserId)
                        .build()));
    }

    private String exchangeCodeForToken(String code) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);

        MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
        params.add("client_id", clientId);
        params.add("client_secret", clientSecret);
        params.add("grant_type", "authorization_code");
        params.add("redirect_uri", redirectUri);
        params.add("code", code);

        HttpEntity<MultiValueMap<String, String>> request = new HttpEntity<>(params, headers);
        ResponseEntity<Map> response = restTemplate.postForEntity(tokenUrl, request, Map.class);

        if (!response.getStatusCode().is2xxSuccessful() || response.getBody() == null) {
            throw new RuntimeException("Instagram token exchange failed");
        }
        return (String) response.getBody().get("access_token");
    }

    private String exchangeForLongLivedToken(String shortToken) {
        String url = longLivedTokenUrl
                + "?grant_type=ig_exchange_token"
                + "&client_secret=" + clientSecret
                + "&access_token=" + shortToken;

        ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
        if (!response.getStatusCode().is2xxSuccessful() || response.getBody() == null) {
            throw new RuntimeException("Instagram long-lived token exchange failed");
        }
        return (String) response.getBody().get("access_token");
    }

    private JsonNode fetchInstagramProfile(String accessToken) {
        String url = profileUrl + "?fields=id,username&access_token=" + accessToken;
        ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
        try {
            return objectMapper.readTree(response.getBody());
        } catch (Exception e) {
            throw new RuntimeException("Failed to parse Instagram profile", e);
        }
    }
}
