import json
from datetime import datetime, timezone, timedelta, date
from sqlalchemy.orm import Session
from app import models, auth
from app.core.logging_config import logger

DEMO_USER_EMAIL = "maya.lin@berkeley.edu"
DEMO_USERNAME = "maya_lin"
DEMO_PASSWORD = "DemoStudent2025!"

def get_or_create_demo_user(db: Session) -> models.User:
    """
    Retrieves or safely seeds the isolated demo student 'Maya Lin'.
    Never alters, deletes, or touches any other user's records.
    """
    user = db.query(models.User).filter(models.User.email == DEMO_USER_EMAIL).first()
    if user:
        return user

    logger.info("Initializing isolated demo student Maya Lin (CS162 / Distributed Systems)")

    # 1. Create Demo User
    user = models.User(
        name="Maya Lin",
        username=DEMO_USERNAME,
        email=DEMO_USER_EMAIL,
        password_hash=auth.hash_password(DEMO_PASSWORD),
        target_role="Software Engineer — Distributed Systems & Cloud Infrastructure",
        skill_level="ADVANCED",
        learning_goals="Master distributed systems consensus invariants, kernel address spaces, and fault-tolerant cloud architecture before upcoming midterms and FAANG interviews.",
        hours_per_day=2.5,
        days_per_week=6,
        experience_level="INTERMEDIATE",
        current_skills=json.dumps(["Distributed Systems", "Go", "Python", "Rust", "Docker", "Kubernetes", "Linux Internals"]),
        preferred_areas=json.dumps(["Distributed Systems", "Cloud Infrastructure", "Concurrency & OS"]),
        onboarding_completed=True,
        created_at=datetime.now(timezone.utc) - timedelta(days=45)
    )
    db.add(user)
    db.flush()

    # 2. Daily Study Streak (14 Days)
    streak = models.Streak(
        user_id=user.id,
        current_streak=14,
        longest_streak=19,
        last_activity_date=date.today()
    )
    db.add(streak)

    # 3. Ensure Curricula & Topics exist for Distributed Systems & OS
    curr_sys = db.query(models.Curriculum).filter(models.Curriculum.name == "Distributed Systems & Systems OS").first()
    if not curr_sys:
        curr_sys = models.Curriculum(
            name="Distributed Systems & Systems OS",
            description="Core Berkeley CS162 and MIT 6.824 systems principles",
            difficulty="advanced"
        )
        db.add(curr_sys)
        db.flush()

    topic_defs = [
        ("Distributed Systems: Raft Consensus", "Master leader elections, randomized timers, log replication, and quorum safety."),
        ("Physical Memory Allocators", "Buddy allocators, slab caches, and page-frame management."),
        ("Concurrency & Mutex Locks", "Mutexes, condition variables, spinlocks, and cache-coherency barriers."),
        ("File Systems & Inodes", "Crash consistency, journaled file systems, ext4 inodes, and soft updates."),
        ("Virtual Memory Paging & TLB", "Multi-level page tables, TLB shootdowns, and hardware address translation."),
        ("Deadlock Avoidance & Banker's Algorithm", "Safe vs unsafe states, resource allocation graphs, and Bankers algorithm."),
        ("QuickSort Worst-Case & Randomized Pivot", "Pivot selection, recursion depth bounds, and O(n log n) expected time."),
        ("B-Tree Balancing & Two-Phase Locking", "Concurrent B+ tree traversal, crab locking, and strict 2PL transaction isolation."),
        ("TCP Congestion Control & Slow Start", "Additive Increase Multiplicative Decrease, BBR, and window sizing.")
    ]

    created_topics = {}
    for name, desc in topic_defs:
        top = db.query(models.Topic).filter(models.Topic.name == name).first()
        if not top:
            top = models.Topic(
                name=name,
                description=desc,
                category="Distributed Systems & OS",
                curriculum_id=curr_sys.id
            )
            db.add(top)
            db.flush()
        created_topics[name] = top

    # 4. Evaluations (Creates an 84% average cognitive mastery with strong & gap areas)
    eval_specs = [
        ("Physical Memory Allocators", 93, 94, 91, "Superb mastery of slab allocators and page fragmentation mitigations."),
        ("Concurrency & Mutex Locks", 88, 90, 86, "Excellent explanation of condition variable wait loops and memory barriers."),
        ("File Systems & Inodes", 82, 85, 80, "Solid explanation of journaling and write-ahead log flush order."),
        ("Distributed Systems: Raft Consensus", 86, 88, 84, "Strong understanding of leader completeness and randomized election timers."),
        ("Virtual Memory Paging & TLB", 54, 52, 58, "Confusing page table walk with TLB hit latency and process switch TLB flushing."),
        ("Deadlock Avoidance & Banker's Algorithm", 58, 56, 62, "Difficulty articulating safety vector verification under multi-resource allocation constraints.")
    ]

    for topic_name, score, tech_score, comm_score, feedback_text in eval_specs:
        topic_obj = created_topics.get(topic_name)
        if topic_obj:
            evaluation = models.Evaluation(
                user_id=user.id,
                topic_id=topic_obj.id,
                explanation=f"Demonstration of {topic_name} core mechanics, invariants, and edge cases.",
                ai_score=score,
                overall_score=score,
                technical_score=tech_score,
                concept_score=score,
                communication_score=comm_score,
                completeness_score=score,
                relevance_score=score,
                speaking_pace_score=85,
                clarity_score=comm_score,
                filler_words=2,
                ai_insight=feedback_text,
                ai_feedback_json=json.dumps({
                    "score": score,
                    "strengths": [f"Clear conceptual grasp of {topic_name} fundamentals.", "Precise technical vocabulary used."],
                    "weaknesses": [feedback_text],
                    "recommendations": [f"Review advanced partition handling and edge cases in {topic_name}."]
                }),
                created_at=datetime.now(timezone.utc) - timedelta(days=2)
            )
            db.add(evaluation)

            # User Mastery
            mastery = models.UserMastery(
                user_id=user.id,
                topic_id=topic_obj.id,
                mastery_score=float(score),
                attempts=3,
                successful_attempts=2 if score >= 70 else 1,
                failed_attempts=0 if score >= 70 else 1,
                last_review=datetime.now(timezone.utc) - timedelta(days=2),
                next_review=datetime.now(timezone.utc) + timedelta(days=3)
            )
            db.add(mastery)

    # 5. Learning Activities (Logged for consistency trend)
    for i in range(14):
        act_date = date.today() - timedelta(days=i)
        db.add(models.LearningActivity(
            user_id=user.id,
            activity_type="explanation" if i % 2 == 0 else "revision",
            date_logged=act_date,
            created_at=datetime.now(timezone.utc) - timedelta(days=i)
        ))

    # 6. Revision Schedules
    rev_specs = [
        ("QuickSort Worst-Case & Randomized Pivot", 72.0, "DUE", 1),
        ("B-Tree Balancing & Two-Phase Locking", 68.0, "UPCOMING", 2),
        ("TCP Congestion Control & Slow Start", 75.0, "UPCOMING", 3)
    ]
    for topic_name, score, status, offset in rev_specs:
        top = created_topics.get(topic_name)
        if top:
            db.add(models.RevisionSchedule(
                user_id=user.id,
                topic_id=top.id,
                last_mastery_score=score - 10,
                current_mastery_score=score,
                last_reviewed_at=datetime.now(timezone.utc) - timedelta(days=4),
                next_review_at=datetime.now(timezone.utc) + timedelta(days=offset),
                review_count=3,
                status=status
            ))

    # 7. AI Resume Intelligence (86% Match Score)
    resume = models.Resume(
        user_id=user.id,
        file_name="resume_maya_lin_2025.pdf",
        file_type="pdf",
        file_path="uploads/resumes/demo_maya_lin_resume.pdf",
        extracted_text="Maya Lin | UC Berkeley Computer Science & Data Intelligence 2027. Software Engineering Intern at Velocity Cloud Networks...",
        is_active=True,
        parsed_skills=json.dumps(["Distributed Systems", "Go", "Rust", "C++", "Python", "Raft Consensus", "Docker", "Kubernetes", "Linux eBPF", "PostgreSQL"]),
        parsed_projects=json.dumps([
            {
                "title": "Distributed Key-Value Store with LSM-Tree Engine",
                "technologies": ["Go", "Raft", "gRPC", "Protobuf"],
                "description": "Implemented Raft-based distributed key-value store with log replication, snapshots, and membership changes. Handled 15k+ req/sec with <45ms p99 latency."
            },
            {
                "title": "eBPF Packet Filter & Linux Kernel Bridge",
                "technologies": ["C", "Linux Kernel", "eBPF"],
                "description": "Engineered kernel bypass packet monitoring with zero memory copying and drop-rate telemetry."
            }
        ]),
        parsed_experience=json.dumps([
            {
                "company": "Velocity Cloud Networks",
                "role": "Software Engineering Intern — Core Storage Infrastructure",
                "period": "Summer 2025",
                "bullets": [
                    "Engineered automated schema migration pipelines in Go, eliminating schema rollback errors across 45+ distributed storage nodes with zero downtime.",
                    "Improved Raft election failover convergence from 650ms to 120ms under packet drop chaos benchmarks."
                ]
            }
        ]),
        parsed_education=json.dumps([
            {
                "institution": "University of California, Berkeley",
                "degree": "B.S. Computer Science & Data Science",
                "graduation": "Spring 2027",
                "gpa": "3.92"
            }
        ]),
        analysis_summary_json=json.dumps({
            "match_score": 86,
            "target_role": "Software Engineer — Distributed Systems & Cloud Infrastructure",
            "percentile": "Top 8% percentile candidate profile for Google, Databricks, and Stripe benchmarks.",
            "ats_parsability": "99.4% OCR precision",
            "strengths": [
                "Strong Systems Programming Experience: Multi-raft replication and high-throughput LSM-Tree work in Rust and Go.",
                "Quantified Impact Metrics: Exemplary +24% throughput boost and 650ms to 120ms failover recovery measurements.",
                "Robust Academic Foundation: UC Berkeley CS & Data Intelligence with 3.92 GPA.",
                "High ATS Parsability: Clean hierarchical section tags with 99.4% OCR precision."
            ],
            "missing_skills": [
                {"name": "Distributed Tracing & Observability", "status": "Missing", "detail": "Target roles at Databricks and Stripe require OpenTelemetry or Jaeger pipeline exposure."},
                {"name": "CI/CD & Deployment Automation", "status": "Needs Detail", "detail": "GitHub Actions, ArgoCD, or Helm configuration is missing from project items."},
                {"name": "Concurrency & Race Condition Testing", "status": "Inter-Quantified", "detail": "Target JDs prioritize ThreadSanitizer or TSan race detection testing."}
            ],
            "skills_comparison": [
                {"skill": "Distributed Systems & Consensus", "candidate": 95, "target": 85},
                {"skill": "Systems Languages (Go, C++, Rust)", "candidate": 92, "target": 90},
                {"skill": "Distributed Tracing & Observability", "candidate": 48, "target": 70},
                {"skill": "CI/CD & Infrastructure as Code", "candidate": 52, "target": 75}
            ],
            "anticipated_probes": [
                "System Design: High-Throughput Write Engine — How did you prevent cascading failover during distributed node partition?",
                "Concurrency: Raft Split-Brain Quorum — How did you handle asymmetric network partitions across multi-AZ deployments?"
            ],
            "suggestions": [
                {
                    "original": "Helped team build database schema migrations and handled test runs for storage cluster deployment automation.",
                    "optimized": "Engineered automated schema migration pipelines in Go, eliminating schema rollback errors across 45+ distributed storage nodes with zero downtime.",
                    "lift": "+25 Impact Lift"
                },
                {
                    "original": "Worked on backend API using Go and PostgreSQL.",
                    "optimized": "Architected high-throughput RESTful & gRPC services in Go, handling 15,000+ req/sec with <45ms p99 latency and OpenTelemetry distributed tracing.",
                    "lift": "+18% ATS Lift"
                }
            ]
        })
    )
    db.add(resume)

    # 8. Mock Interview Simulation (88% Overall Score)
    interview = models.Interview(
        user_id=user.id,
        target_role="Software Engineer — Distributed Systems & Architecture Round",
        difficulty="HARD",
        interview_type="technical",
        starting_difficulty="HARD",
        current_difficulty="HARD",
        question_count=3,
        current_question_number=3,
        status="COMPLETED",
        overall_score=88,
        technical_score=90,
        communication_score=88,
        project_knowledge_score=87,
        problem_solving_score=86,
        feedback_json=json.dumps({
            "overall_score": 88,
            "benchmark": "Senior L5 Bar",
            "communication_strengths": [
                "Structured MECE response: Clearly decomposed system into edge gateways, rate-limiting worker pools, and shared data tiers.",
                "Optimal speaking pace: Maintained a calm, articulate cadence of 135 wpm with minimal filler pauses."
            ],
            "improvement_areas": [
                "Cache latency trade-offs: Mentioned cache eviction policies but omitted write-through vs write-back latency trade-offs during cross-AZ synchronization.",
                "Failure recovery: Could explicitly address partition reassignment if an active coordinator node fails under backpressure."
            ],
            "metrics": {
                "speaking_pace": "135 wpm (Optimal)",
                "clarity": "92%",
                "filler_words": 2,
                "grammar": "94%"
            }
        }),
        started_at=datetime.now(timezone.utc) - timedelta(days=1),
        completed_at=datetime.now(timezone.utc) - timedelta(days=1, hours=-1)
    )
    db.add(interview)
    db.flush()

    # Question for interview
    int_q = models.InterviewQuestion(
        interview_id=interview.id,
        question_number=1,
        question_text="Design a fault-tolerant distributed rate limiter capable of handling 50,000 requests per second across 3 availability zones.",
        category="SYSTEM_DESIGN",
        difficulty="HARD"
    )
    db.add(int_q)
    db.flush()

    int_a = models.InterviewAnswer(
        question_id=int_q.id,
        answer_text="To design a distributed rate limiter handling 50,000 RPS across 3 AZs, I recommend a tiered Token Bucket architecture with local in-memory token buckets at edge Envoy proxies and asynchronous sync via Redis Cluster / Raft...",
        ai_score=88,
        technical_score=90,
        communication_score=88,
        overall_score=88,
        feedback="Exemplary answer demonstrating strong architectural judgment and multi-AZ failover awareness."
    )
    db.add(int_a)
    db.flush()

    # Communication analysis
    db.add(models.CommunicationAnalysis(
        user_id=user.id,
        interview_id=interview.id,
        answer_id=int_a.id,
        communication_score=88,
        clarity_score=92,
        grammar_score=94,
        vocabulary_score=90,
        structure_score=92,
        speaking_pace="Good",
        words_per_minute=135,
        pause_count=3,
        filler_word_count=2,
        filler_words_json=json.dumps({"um": 1, "like": 1}),
        grammar_feedback="Grammatically pristine. Technical descriptors used with precision.",
        ai_coach_recommendation="Continue maintaining this steady pacing and MECE framework."
    ))

    # 9. Virtual Study Sessions
    if created_topics.get("Distributed Systems: Raft Consensus"):
        db.add(models.StudySession(
            user_id=user.id,
            topic_id=created_topics["Distributed Systems: Raft Consensus"].id,
            created_at=datetime.now(timezone.utc) - timedelta(hours=3)
        ))

    db.commit()
    db.refresh(user)
    logger.info(f"Isolated demo student Maya Lin successfully initialized (User ID: {user.id})")
    return user
