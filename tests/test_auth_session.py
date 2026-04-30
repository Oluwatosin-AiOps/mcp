from app.auth_session import SessionAuthState


def test_sensitive_tool_blocked_until_verify():
    auth = SessionAuthState()
    ok, msg, args = auth.prepare_tool_call("list_orders", {})
    assert not ok
    assert "verify_customer_pin" in msg


def test_verify_success_records_customer_id():
    auth = SessionAuthState()
    body = "Verified customer Jane Doe\nCustomer ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890\n"
    auth.record_verify_customer_pin_result(body)
    assert auth.verified_customer_id == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"


def test_verify_failure_does_not_record():
    auth = SessionAuthState()
    auth.record_verify_customer_pin_result("CustomerNotFoundError: PIN incorrect")
    assert auth.verified_customer_id is None


def test_list_orders_injects_customer_id():
    auth = SessionAuthState()
    auth.record_verify_customer_pin_result(
        "OK id 11111111-2222-3333-4444-555555555555 end"
    )
    ok, msg, args = auth.prepare_tool_call("list_orders", {})
    assert ok
    assert msg == ""
    assert args["customer_id"] == "11111111-2222-3333-4444-555555555555"


def test_list_orders_rejects_other_customer():
    auth = SessionAuthState()
    auth.record_verify_customer_pin_result(
        "OK id 11111111-2222-3333-4444-555555555555 end"
    )
    ok, msg, _ = auth.prepare_tool_call(
        "list_orders",
        {"customer_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"},
    )
    assert not ok


def test_create_order_must_match_verified():
    auth = SessionAuthState()
    auth.record_verify_customer_pin_result(
        "OK id 11111111-2222-3333-4444-555555555555 end"
    )
    ok, _, _ = auth.prepare_tool_call(
        "create_order",
        {"customer_id": "11111111-2222-3333-4444-555555555555", "items": []},
    )
    assert ok
    ok2, msg2, _ = auth.prepare_tool_call(
        "create_order",
        {"customer_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", "items": []},
    )
    assert not ok2


def test_product_tools_never_blocked():
    auth = SessionAuthState()
    ok, _, _ = auth.prepare_tool_call("search_products", {"query": "keyboard"})
    assert ok


def test_create_order_injects_customer_id_when_missing():
    auth = SessionAuthState()
    auth.record_verify_customer_pin_result(
        "OK id 11111111-2222-3333-4444-555555555555 end"
    )
    ok, _, args = auth.prepare_tool_call(
        "create_order",
        {"items": [{"sku": "MON-1", "quantity": 1, "unit_price": 10.0}]},
    )
    assert ok
    assert args["customer_id"] == "11111111-2222-3333-4444-555555555555"


def test_get_customer_injects_customer_id_when_missing():
    auth = SessionAuthState()
    auth.record_verify_customer_pin_result(
        "OK id 11111111-2222-3333-4444-555555555555 end"
    )
    ok, _, args = auth.prepare_tool_call("get_customer", {})
    assert ok
    assert args["customer_id"] == "11111111-2222-3333-4444-555555555555"


def test_get_customer_rejects_other_customer_when_provided():
    auth = SessionAuthState()
    auth.record_verify_customer_pin_result(
        "OK id 11111111-2222-3333-4444-555555555555 end"
    )
    ok, msg, _ = auth.prepare_tool_call(
        "get_customer",
        {"customer_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"},
    )
    assert not ok
    assert "verified" in msg.lower()
