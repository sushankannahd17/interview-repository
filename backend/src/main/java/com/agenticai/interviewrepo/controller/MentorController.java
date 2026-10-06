package com.agenticai.interviewrepo.controller;

import com.agenticai.interviewrepo.dto.InterviewExperienceResponse;
import com.agenticai.interviewrepo.dto.MentorProfileRequest;
import com.agenticai.interviewrepo.dto.MentorProfileResponse;
import com.agenticai.interviewrepo.dto.StudentProfileResponse;
import com.agenticai.interviewrepo.service.MentorService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/mentor")
public class MentorController {

    private final MentorService mentorService;

    public MentorController(MentorService mentorService) {
        this.mentorService = mentorService;
    }

    @GetMapping("/profile")
    public ResponseEntity<MentorProfileResponse> getProfile() {
        return ResponseEntity.ok(mentorService.getMyProfile());
    }

    @PutMapping("/profile")
    public ResponseEntity<MentorProfileResponse> updateProfile(
            @RequestBody MentorProfileRequest request
    ) {
        return ResponseEntity.ok(mentorService.updateMyProfile(request));
    }

    @GetMapping("/mentees")
    public ResponseEntity<List<StudentProfileResponse>> getMentees() {
        return ResponseEntity.ok(mentorService.getMentees());
    }

    @GetMapping("/mentees/{studentId}")
    public ResponseEntity<StudentProfileResponse> getMenteeDetail(@PathVariable UUID studentId) {
        return ResponseEntity.ok(mentorService.getMenteeDetail(studentId));
    }

    @GetMapping("/mentees/{studentId}/experiences")
    public ResponseEntity<List<InterviewExperienceResponse>> getMenteeExperiences(@PathVariable UUID studentId) {
        return ResponseEntity.ok(mentorService.getMenteeExperiences(studentId));
    }

    @GetMapping("/available-students")
    public ResponseEntity<List<StudentProfileResponse>> getAvailableStudents() {
        return ResponseEntity.ok(mentorService.getAvailableStudents());
    }

    @PostMapping("/mentees/{studentId}/assign")
    public ResponseEntity<StudentProfileResponse> assignMentee(@PathVariable UUID studentId) {
        return ResponseEntity.ok(mentorService.assignMentee(studentId));
    }
}