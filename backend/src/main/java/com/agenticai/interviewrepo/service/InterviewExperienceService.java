package com.agenticai.interviewrepo.service;

import com.agenticai.interviewrepo.dto.InterviewExperienceRequest;
import com.agenticai.interviewrepo.dto.InterviewExperienceResponse;
import com.agenticai.interviewrepo.dto.ModerationRequest;
import com.agenticai.interviewrepo.model.*;
import com.agenticai.interviewrepo.repository.*;
import jakarta.transaction.Transactional;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Service
public class InterviewExperienceService {
    private final InterviewExperienceRepository experiences;
    private final CompanyRepository companies;
    private final StudentRepository students;
    private final AlumniRepository alumni;
    private final AdministratorRepository administrators;
    private final ModerationLogRepository moderationLogs;
    private final CurrentUserService currentUser;

    public InterviewExperienceService(InterviewExperienceRepository experiences,
            CompanyRepository companies, StudentRepository students, AlumniRepository alumni,
            AdministratorRepository administrators, ModerationLogRepository moderationLogs,
            CurrentUserService currentUser) {
        this.experiences = experiences; this.companies = companies; this.students = students;
        this.alumni = alumni; this.administrators = administrators; this.moderationLogs = moderationLogs;
        this.currentUser = currentUser;
    }

    private Company resolveCompany(UUID companyId, String companyName) {
        if (companyId != null) {
            Company c = companies.findById(companyId).orElse(null);
            if (c != null) return c;
        }
        if (companyName != null && !companyName.isBlank()) {
            String name = companyName.trim();
            return companies.findByNameIgnoreCase(name)
                    .orElseGet(() -> {
                        Company newComp = new Company();
                        newComp.setName(name);
                        return companies.save(newComp);
                    });
        }
        throw new IllegalArgumentException("Company is required (provide companyId or companyName)");
    }

    @Transactional
    public InterviewExperienceResponse create(InterviewExperienceRequest request) {
        if (!Boolean.TRUE.equals(request.getConsentGiven()))
            throw new IllegalArgumentException("Consent must be given before submitting an interview experience");
        validateOrdering(request);
        User submitter = currentUser.getCurrentUser();
        InterviewExperience value = new InterviewExperience();
        value.setSubmittedBy(submitter);
        value.setCompany(resolveCompany(request.getCompanyId(), request.getCompanyName()));
        students.findByLogin(submitter).ifPresent(value::setStudent);
        alumni.findByLogin(submitter).ifPresent(value::setAlumni);
        value.setRole(request.getRole()); value.setInterviewDate(request.getInterviewDate());
        value.setDifficulty(request.getDifficulty()); value.setExperience(request.getExperience());
        value.setQuestionsSummary(request.getQuestionsSummary()); value.setTips(request.getTips());
        value.setInterviewResult(request.getInterviewResult()); value.setProvenance(request.getProvenance());
        value.setPreparation(request.getPreparation()); value.setTimeline(request.getTimeline());
        value.setConsentGiven(true); value.setConsentAt(LocalDateTime.now());
        value.setSubmittedAt(LocalDateTime.now()); value.setModerationStatus("PENDING");
        if (request.getRounds() != null) {
            for (InterviewExperienceRequest.RoundRequest roundRequest : request.getRounds()) {
                InterviewRound round = new InterviewRound();
                round.setRoundOrder(roundRequest.getRoundOrder()); round.setName(roundRequest.getName());
                round.setNotes(roundRequest.getNotes()); value.addRound(round);
                if (roundRequest.getQuestions() != null) {
                    for (InterviewExperienceRequest.QuestionRequest questionRequest : roundRequest.getQuestions()) {
                        Question question = new Question();
                        question.setQuestionOrder(questionRequest.getQuestionOrder());
                        question.setQuestionText(questionRequest.getQuestionText());
                        question.setTopic(questionRequest.getTopic()); question.setDifficulty(questionRequest.getDifficulty());
                        question.setInterview(value); round.addQuestion(question);
                    }
                }
            }
        }
        return InterviewExperienceResponse.from(experiences.save(value));
    }

    @Transactional
    public List<InterviewExperienceResponse> getMyExperiences() {
        User submitter = currentUser.getCurrentUser();
        return experiences.findBySubmittedByOrderBySubmittedAtDesc(submitter)
                .stream().map(InterviewExperienceResponse::from).toList();
    }

    @Transactional
    public List<InterviewExperienceResponse> getStudentExperiences(UUID studentId) {
        return experiences.findByStudentIdOrderBySubmittedAtDesc(studentId)
                .stream().map(InterviewExperienceResponse::from).toList();
    }

    @Transactional
    public InterviewExperienceResponse update(UUID id, InterviewExperienceRequest request) {
        InterviewExperience value = experiences.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Interview experience not found"));
        User user = currentUser.getCurrentUser();
        if (user.getRole() != Role.ADMIN && (value.getSubmittedBy() == null || !value.getSubmittedBy().getId().equals(user.getId()))) {
            throw new AccessDeniedException("You do not have permission to edit this experience");
        }
        if (request.getRole() != null) value.setRole(request.getRole());
        if (request.getCompanyId() != null || (request.getCompanyName() != null && !request.getCompanyName().isBlank())) {
            value.setCompany(resolveCompany(request.getCompanyId(), request.getCompanyName()));
        }
        if (request.getInterviewDate() != null) value.setInterviewDate(request.getInterviewDate());
        if (request.getDifficulty() != null) value.setDifficulty(request.getDifficulty());
        if (request.getExperience() != null) value.setExperience(request.getExperience());
        if (request.getQuestionsSummary() != null) value.setQuestionsSummary(request.getQuestionsSummary());
        if (request.getTips() != null) value.setTips(request.getTips());
        if (request.getInterviewResult() != null) value.setInterviewResult(request.getInterviewResult());
        if (request.getProvenance() != null) value.setProvenance(request.getProvenance());
        if (request.getPreparation() != null) value.setPreparation(request.getPreparation());
        if (request.getTimeline() != null) value.setTimeline(request.getTimeline());

        if (request.getRounds() != null && !request.getRounds().isEmpty()) {
            validateOrdering(request);
            value.getRounds().clear();
            for (InterviewExperienceRequest.RoundRequest roundRequest : request.getRounds()) {
                InterviewRound round = new InterviewRound();
                round.setRoundOrder(roundRequest.getRoundOrder());
                round.setName(roundRequest.getName());
                round.setNotes(roundRequest.getNotes());
                value.addRound(round);
                if (roundRequest.getQuestions() != null) {
                    for (InterviewExperienceRequest.QuestionRequest questionRequest : roundRequest.getQuestions()) {
                        Question question = new Question();
                        question.setQuestionOrder(questionRequest.getQuestionOrder());
                        question.setQuestionText(questionRequest.getQuestionText());
                        question.setTopic(questionRequest.getTopic());
                        question.setDifficulty(questionRequest.getDifficulty());
                        question.setInterview(value);
                        round.addQuestion(question);
                    }
                }
            }
        }
        return InterviewExperienceResponse.from(experiences.save(value));
    }

    @Transactional
    public void delete(UUID id) {
        InterviewExperience value = experiences.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Interview experience not found"));
        User user = currentUser.getCurrentUser();
        if (user.getRole() != Role.ADMIN && (value.getSubmittedBy() == null || !value.getSubmittedBy().getId().equals(user.getId()))) {
            throw new AccessDeniedException("You do not have permission to delete this experience");
        }
        experiences.delete(value);
    }

    @Transactional
    public InterviewExperienceResponse moderate(UUID id, ModerationRequest request) {
        if (!SetOfStatuses.contains(request.getModerationStatus()))
            throw new IllegalArgumentException("moderationStatus must be PENDING, APPROVED, or REJECTED");
        InterviewExperience value = experiences.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Interview experience not found"));
        User adminUser = currentUser.getCurrentUser();
        value.setModerationStatus(request.getModerationStatus());
        value.setStatus(request.getModerationStatus());
        
        administrators.findByLogin(adminUser)
                .or(() -> {
                    Administrator admin = new Administrator();
                    admin.setLogin(adminUser);
                    admin.setName(adminUser.getName() != null && !adminUser.getName().isBlank() ? adminUser.getName() : adminUser.getEmail());
                    return Optional.of(administrators.save(admin));
                })
                .ifPresent(admin -> {
                    ModerationLog log = new ModerationLog();
                    log.setAdmin(admin); log.setEntityType("INTERVIEW_EXPERIENCE"); log.setEntityId(id);
                    log.setAction(request.getModerationStatus()); log.setReason(request.getReason());
                    moderationLogs.save(log);
                });
        return InterviewExperienceResponse.from(value);
    }

    @Transactional
    public InterviewExperienceResponse get(UUID id) {
        return InterviewExperienceResponse.from(experiences.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Interview experience not found")));
    }

    @Transactional
    public Page<InterviewExperienceResponse> list(UUID companyId, boolean includeUnmoderated, Pageable pageable) {
        Page<InterviewExperience> page = includeUnmoderated
                ? (companyId == null ? experiences.findAll(pageable)
                    : experiences.findByCompanyId(companyId, pageable))
                : (companyId == null ? experiences.findByModerationStatus("APPROVED", pageable)
                    : experiences.findByModerationStatusAndCompanyId("APPROVED", companyId, pageable));
        return page.map(InterviewExperienceResponse::from);
    }

    public boolean isAdmin() {
        return currentUser.getCurrentUser().getRole() == Role.ADMIN;
    }

    private void validateOrdering(InterviewExperienceRequest request) {
        if (request.getRounds() == null) return;
        HashSet<Integer> roundOrders = new HashSet<>();
        for (InterviewExperienceRequest.RoundRequest round : request.getRounds()) {
            if (!roundOrders.add(round.getRoundOrder())) throw new IllegalArgumentException("Round order values must be unique");
            if (round.getQuestions() != null) {
                HashSet<Integer> questionOrders = new HashSet<>();
                for (InterviewExperienceRequest.QuestionRequest question : round.getQuestions())
                    if (!questionOrders.add(question.getQuestionOrder()))
                        throw new IllegalArgumentException("Question order values must be unique within a round");
            }
        }
    }

    private static final class SetOfStatuses {
        static boolean contains(String value) { return "PENDING".equals(value) || "APPROVED".equals(value) || "REJECTED".equals(value); }
    }
}