package com.agenticai.interviewrepo.dto;

import java.util.UUID;

public class AdminAssignMentorRequest {
    private UUID mentorId;

    public UUID getMentorId() {
        return mentorId;
    }

    public void setMentorId(UUID mentorId) {
        this.mentorId = mentorId;
    }
}
