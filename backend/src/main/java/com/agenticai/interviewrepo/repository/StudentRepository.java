// StudentRepository.java
package com.agenticai.interviewrepo.repository;

import com.agenticai.interviewrepo.model.Mentor;
import com.agenticai.interviewrepo.model.Student;
import com.agenticai.interviewrepo.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface StudentRepository extends JpaRepository<Student, UUID> {
    Optional<Student> findByLogin(User login);
    List<Student> findByMentor(Mentor mentor);
    List<Student> findByMentorId(UUID mentorId);
    List<Student> findByMentorIsNull();
}