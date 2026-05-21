package com.bnipost.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserProfile {
    private Long id;
    private String email;
    private String nickname;
    private String profileImage;
    private String provider;
    private boolean hasNaverToken;
    private boolean hasInstagramToken;
}
