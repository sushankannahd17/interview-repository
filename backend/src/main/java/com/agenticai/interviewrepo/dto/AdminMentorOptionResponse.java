package com.agenticai.interviewrepo.dto;

import java.util.UUID;

public class AdminMentorOptionResponse {
    private UUID id;
    private UUID loginId;
    private String name;
    private String email;
    private String expertise;

    public AdminMentorOptionResponse() {}
    public AdminMentorOptionResponse(UUID id, UUID loginId, String name, String email, String expertise) {
        this.id = id;
        this.loginId = loginId;
        this.name = name;
        this.email = email;
        this.expertise = expertise;
    }

    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }
    public UUID getLoginId() { return loginId; }
    public void setLoginId(UUID loginId) { this.loginId = loginId; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getExpertise() { return expertise; }
    public void setExpertise(String expertise) { this.expertise = expertise; }
}
