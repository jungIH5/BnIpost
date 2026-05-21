package com.bnipost.repository;

import com.bnipost.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByProviderAndProviderId(User.Provider provider, String providerId);
    Optional<User> findByEmail(String email);
}
