package com.bnipost.controller;

import com.bnipost.dto.TokenResponse;
import com.bnipost.dto.UserProfile;
import com.bnipost.entity.User;
import com.bnipost.service.InstagramOAuthService;
import com.bnipost.service.NaverOAuthService;
import com.bnipost.util.JwtUtil;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;

@Slf4j
@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final NaverOAuthService naverOAuthService;
    private final InstagramOAuthService instagramOAuthService;
    private final JwtUtil jwtUtil;

    @Value("${app.frontend-url:http://localhost:3000}")
    private String frontendUrl;

    // Naver OAuth start
    @GetMapping("/naver")
    public void naverLogin(HttpServletResponse response) throws IOException {
        String state = naverOAuthService.generateState();
        String redirectUrl = naverOAuthService.buildAuthorizationUrl(state);
        response.sendRedirect(redirectUrl);
    }

    // Naver OAuth callback
    @GetMapping("/naver/callback")
    public void naverCallback(@RequestParam String code,
                              @RequestParam String state,
                              HttpServletResponse response) throws IOException {
        try {
            User user = naverOAuthService.processCallback(code, state);
            String token = jwtUtil.generateToken(user.getId(), user.getEmail(), user.getNickname());
            response.sendRedirect(frontendUrl + "/auth/callback?token=" + token);
        } catch (Exception e) {
            log.error("Naver OAuth callback error", e);
            response.sendRedirect(frontendUrl + "/login?error=naver_failed");
        }
    }

    // Instagram OAuth start
    @GetMapping("/instagram")
    public void instagramLogin(HttpServletResponse response) throws IOException {
        String redirectUrl = instagramOAuthService.buildAuthorizationUrl();
        response.sendRedirect(redirectUrl);
    }

    // Instagram OAuth callback
    @GetMapping("/instagram/callback")
    public void instagramCallback(@RequestParam String code,
                                  HttpServletResponse response) throws IOException {
        try {
            User user = instagramOAuthService.processCallback(code);
            String token = jwtUtil.generateToken(user.getId(), user.getEmail(), user.getNickname());
            response.sendRedirect(frontendUrl + "/auth/callback?token=" + token);
        } catch (Exception e) {
            log.error("Instagram OAuth callback error", e);
            response.sendRedirect(frontendUrl + "/login?error=instagram_failed");
        }
    }
}
