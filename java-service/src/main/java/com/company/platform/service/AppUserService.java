package com.company.platform.service;

import com.company.platform.domain.AppUser;
import com.company.platform.repository.AppUserRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class AppUserService {

    private final AppUserRepository appUserRepository;

    public AppUserService(AppUserRepository appUserRepository) {
        this.appUserRepository = appUserRepository;
    }

    public List<AppUser> findAll() {
        return appUserRepository.findAll();
    }

    public AppUser create(AppUser appUser) {
        appUserRepository.findByEmail(appUser.getEmail()).ifPresent(u -> {
            throw new IllegalArgumentException("Email already exists");
        });
        return appUserRepository.save(appUser);
    }
}
