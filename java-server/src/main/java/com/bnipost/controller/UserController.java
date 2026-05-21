package com.bnipost.controller;

import com.bnipost.dto.UserProfile;
import com.bnipost.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping("/me")
    public ResponseEntity<UserProfile> getProfile(@AuthenticationPrincipal Long userId) {
        return ResponseEntity.ok(userService.getProfile(userId));
    }

    // Internal endpoint called by Python server to retrieve social tokens
    @GetMapping("/internal/token")
    public ResponseEntity<Map<String, String>> getSocialToken(
            @RequestParam Long userId,
            @RequestParam String platform,
            @RequestHeader("X-Internal-Key") String internalKey) {

        String expectedKey = System.getenv().getOrDefault("INTERNAL_API_KEY", "internal-secret");
        if (!expectedKey.equals(internalKey)) {
            return ResponseEntity.status(403).build();
        }

        String token = userService.getSocialToken(userId, platform);
        if (token == null) {
            return ResponseEntity.notFound().build();
        }

        Map<String, String> result = Map.of("token", token);

        if ("instagram".equalsIgnoreCase(platform)) {
            String igUserId = userService.getInstagramUserId(userId);
            if (igUserId != null) {
                result = Map.of("token", token, "instagram_user_id", igUserId);
            }
        }

        return ResponseEntity.ok(result);
    }
}
