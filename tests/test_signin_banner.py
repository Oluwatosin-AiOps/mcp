"""Banner copy for explicit Sign in / Sign out (see ``app/signin.py``)."""

from app.signin import format_auth_banner


def test_banner_not_signed_in():
    assert "Not signed in" in format_auth_banner(None)
    assert "Sign in" in format_auth_banner({"customer_id": None})


def test_banner_signed_in_with_email():
    t = format_auth_banner({"customer_id": "41c2903a-f1a5-47b7-a81d-86b50ade220f", "email": "a@b.co"})
    assert "a@b.co" in t
    assert "Sign out" in t


def test_banner_signed_in_without_email():
    t = format_auth_banner({"customer_id": "41c2903a-f1a5-47b7-a81d-86b50ade220f", "email": None})
    assert "Signed in" in t
    assert "Sign out" in t
