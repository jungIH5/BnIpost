package com.bnipost.service;

import com.bnipost.dto.UserProfile;
import com.bnipost.entity.User;
import com.bnipost.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;

    public UserProfile getProfile(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found: " + userId));
        return toProfile(user);
    }

    public String getSocialToken(Long userId, String platform) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found: " + userId));

        return switch (platform.toLowerCase()) {
            case "naver" -> user.getNaverAccessToken();
            case "instagram" -> user.getInstagramAccessToken();
            default -> throw new IllegalArgumentException("Unknown platform: " + platform);
        };
    }

    public String getInstagramUserId(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found: " + userId));
        return user.getInstagramUserId();
    }

    private UserProfile toProfile(User user) {
        return UserProfile.builder()
                .id(user.getId())
                .email(user.getEmail())
                .nickname(user.getNickname())
                .profileImage(user.getProfileImage())
                .provider(user.getProvider().name())
                .hasNaverToken(user.getNaverAccessToken() != null)
                .hasInstagramToken(user.getInstagramAccessToken() != null)
                .build();
    }
}
