// InterviewExperienceRepository.java
package com.agenticai.interviewrepo.repository;

import com.agenticai.interviewrepo.model.InterviewExperience;
import com.agenticai.interviewrepo.model.PlacedAlumni;
import com.agenticai.interviewrepo.model.Student;
import com.agenticai.interviewrepo.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import java.util.List;
import java.util.UUID;

public interface InterviewExperienceRepository extends JpaRepository<InterviewExperience, UUID> {
    Page<InterviewExperience> findByModerationStatus(String moderationStatus, Pageable pageable);
    Page<InterviewExperience> findByModerationStatusAndCompanyId(String moderationStatus, UUID companyId, Pageable pageable);
    Page<InterviewExperience> findByCompanyId(UUID companyId, Pageable pageable);
    List<InterviewExperience> findBySubmittedByOrderBySubmittedAtDesc(User submittedBy);
    List<InterviewExperience> findByStudentOrderBySubmittedAtDesc(Student student);
    List<InterviewExperience> findByStudentIdOrderBySubmittedAtDesc(UUID studentId);
    List<InterviewExperience> findByAlumniOrderBySubmittedAtDesc(PlacedAlumni alumni);
}