
            a2.answer_text AS correct_answer, sa.is_correct, sa.points_earned
            FROM StudentAnswers sa
            Join accounts a ON sa.student_id = a.account_id