from apps.portfolio_organizer.infrastructure.core.notification_service import NotificationService


def test_send_email(capsys):
    service = NotificationService()
    service.send_email("Test message")
    captured = capsys.readouterr()
    assert "Email sent: Test message" in captured.out


def test_send_email_empty():
    service = NotificationService()
    # Should not raise
    service.send_email("")
