# Backend change notes

## 2026-10-06 — Lombok compiler compatibility

- Maven was running on JDK 27 and compilation failed inside Lombok's javac integration with `ExceptionInInitializerError` involving `com.sun.tools.javac.tree.EndPosTable`.
- Pinned Lombok to 1.18.48 in `pom.xml` for both the application dependency and Maven compiler annotation processor. This release adds JDK 27 support.
- No application source code was changed.
- Verified `./mvnw spring-boot:run`: compilation succeeded, the configured PostgreSQL database connected, and Tomcat started on port 8080. The first run attempt was blocked by the sandbox's network restriction; the approved retry started successfully.
