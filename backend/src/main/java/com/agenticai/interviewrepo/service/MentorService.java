package com.agenticai.interviewrepo.service;

import com.agenticai.interviewrepo.dto.InterviewExperienceResponse;
import com.agenticai.interviewrepo.dto.MentorProfileRequest;
import com.agenticai.interviewrepo.dto.MentorProfileResponse;
import com.agenticai.interviewrepo.dto.StudentProfileResponse;
import com.agenticai.interviewrepo.model.Mentor;
import com.agenticai.interviewrepo.model.Role;
import com.agenticai.interviewrepo.model.Student;
import com.agenticai.interviewrepo.model.User;
import com.agenticai.interviewrepo.repository.InterviewExperienceRepository;
import com.agenticai.interviewrepo.repository.MentorRepository;
import com.agenticai.interviewrepo.repository.StudentRepository;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Service
public class MentorService {

    private final MentorRepository mentorRepository;
    private final StudentRepository studentRepository;
    private final InterviewExperienceRepository experienceRepository;
    private final CurrentUserService currentUserService;

    public MentorService(
            MentorRepository mentorRepository,
            StudentRepository studentRepository,
            InterviewExperienceRepository experienceRepository,
            CurrentUserService currentUserService
    ) {
        this.mentorRepository = mentorRepository;
        this.studentRepository = studentRepository;
        this.experienceRepository = experienceRepository;
        this.currentUserService = currentUserService;
    }

    @Transactional
    public Mentor getCurrentMentor() {
        User user = currentUserService.getCurrentUser();
        return mentorRepository.findByLogin(user)
                .orElseGet(() -> {
                    Mentor newMentor = new Mentor();
                    newMentor.setLogin(user);
                    newMentor.setName(user.getName() != null && !user.getName().isBlank() ? user.getName() : user.getEmail());
                    return mentorRepository.save(newMentor);
                });
    }

    @Transactional
    public MentorProfileResponse getMyProfile() {
        return toResponse(getCurrentMentor());
    }

    @Transactional
    public MentorProfileResponse updateMyProfile(MentorProfileRequest request) {
        User user = currentUserService.getCurrentUser();

        if (user.getRole() != Role.MENTOR && user.getRole() != Role.ADMIN) {
            throw new AccessDeniedException("Only mentors or administrators can modify mentor profiles");
        }

        Mentor mentor = getCurrentMentor();

        if (request.getName() != null) {
            mentor.setName(request.getName());
        }

        if (request.getBio() != null) {
            mentor.setBio(request.getBio());
        }

        if (request.getExpertise() != null) {
            mentor.setExpertise(request.getExpertise());
        }

        return toResponse(mentorRepository.save(mentor));
    }

    @Transactional(readOnly = true)
    public List<StudentProfileResponse> getMentees() {
        Mentor mentor = getCurrentMentor();
        List<Student> mentees = studentRepository.findByMentor(mentor);
        return mentees.stream().map(this::toStudentResponse).toList();
    }

    @Transactional(readOnly = true)
    public StudentProfileResponse getMenteeDetail(UUID studentId) {
        Student student = studentRepository.findById(studentId)
                .orElseThrow(() -> new IllegalArgumentException("Mentee student not found"));
        return toStudentResponse(student);
    }

    @Transactional(readOnly = true)
    public List<InterviewExperienceResponse> getMenteeExperiences(UUID studentId) {
        Student student = studentRepository.findById(studentId)
                .orElseThrow(() -> new IllegalArgumentException("Mentee student not found"));
        return experienceRepository.findByStudentIdOrderBySubmittedAtDesc(student.getId())
                .stream().map(InterviewExperienceResponse::from).toList();
    }

    @Transactional(readOnly = true)
    public List<StudentProfileResponse> getAvailableStudents() {
        return studentRepository.findAll().stream()
                .map(this::toStudentResponse).toList();
    }

    @Transactional
    public StudentProfileResponse assignMentee(UUID studentId) {
        Mentor mentor = getCurrentMentor();
        Student student = studentRepository.findById(studentId)
                .orElseThrow(() -> new IllegalArgumentException("Student not found"));
        student.setMentor(mentor);
        return toStudentResponse(studentRepository.save(student));
    }

    private MentorProfileResponse toResponse(Mentor mentor) {
        MentorProfileResponse response = new MentorProfileResponse();
        response.setId(mentor.getId());
        response.setName(mentor.getName());

        if (mentor.getLogin() != null) {
            response.setEmail(mentor.getLogin().getEmail());
        }

        response.setBio(mentor.getBio());
        response.setExpertise(mentor.getExpertise());
        response.setCreatedAt(mentor.getCreatedAt());
        response.setUpdatedAt(mentor.getUpdatedAt());

        return response;
    }

    private StudentProfileResponse toStudentResponse(Student student) {
        StudentProfileResponse res = new StudentProfileResponse();
        res.setId(student.getId());
        res.setName(student.getName());
        if (student.getLogin() != null) {
            res.setEmail(student.getLogin().getEmail());
        }
        res.setPhone(student.getPhone());
        res.setCollege(student.getCollege());
        res.setDegree(student.getDegree());
        res.setGraduationYear(student.getGraduationYear());
        res.setLinkedinURL(student.getLinkedinUrl());
        res.setResumeURL(student.getResumeUrl());
        res.setGithubURL(student.getGithubUrl());
        res.setSkills(student.getSkills());
        res.setBio(student.getBio());
        if (student.getMentor() != null) {
            res.setMentorID(student.getMentor().getId());
        }
        res.setCreatedAt(student.getCreatedAt());
        res.setUpdatedAt(student.getUpdatedAt());
        return res;
    }
}