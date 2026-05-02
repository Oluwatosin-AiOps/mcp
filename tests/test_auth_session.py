from app.auth_session import SessionAuthState, normalize_session_customer_id


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


def test_failed_verify_does_not_clear_prior_session():
    uid = "11111111-2222-3333-4444-555555555555"
    auth = SessionAuthState(uid)
    auth.record_verify_customer_pin_result("incorrect PIN invalid")
    assert auth.verified_customer_id == uid


def test_prior_verified_allows_orders_without_new_verify():
    uid = "11111111-2222-3333-4444-555555555555"
    auth = SessionAuthState(uid)
    ok, msg, args = auth.prepare_tool_call("list_orders", {})
    assert ok
    assert args["customer_id"] == uid


def test_invalid_prior_session_id_rejected():
    auth = SessionAuthState("not-a-uuid")
    ok, msg, _ = auth.prepare_tool_call("list_orders", {})
    assert not ok
    assert "verify" in msg.lower()


def test_normalize_session_customer_id_accepts_uuid():
    u = "41c2903a-f1a5-47b7-a81d-86b50ade220f"
    assert normalize_session_customer_id(u) == u
    assert normalize_session_customer_id("  " + u + " ") == u
    assert normalize_session_customer_id("nope") is None


def test_list_orders_injects_customer_id():
    auth = SessionAuthState()
    auth.record_verify_customer_pin_result(
        "OK id 11111111-2222-3333-4444-555555555555 end"
    )
    ok, msg, args = auth.prepare_tool_call("list_orders", {})
    assert ok
    assert msg == ""
    assert args["customer_id"] == "11111111-2222-3333-4444-555555555555"


def test_list_orders_overwrites_wrong_model_customer_id():
    uid = "11111111-2222-3333-4444-555555555555"
    auth = SessionAuthState()
    auth.record_verify_customer_pin_result(f"OK id {uid} end")
    ok, msg, args = auth.prepare_tool_call(
        "list_orders",
        {"customer_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"},
    )
    assert ok and msg == ""
    assert args["customer_id"] == uid


def test_create_order_overwrites_wrong_model_customer_id():
    uid = "11111111-2222-3333-4444-555555555555"
    auth = SessionAuthState()
    auth.record_verify_customer_pin_result(f"OK id {uid} end")
    ok, _, args = auth.prepare_tool_call(
        "create_order",
        {"customer_id": uid, "items": []},
    )
    assert ok and args["customer_id"] == uid
    ok2, _, args2 = auth.prepare_tool_call(
        "create_order",
        {"customer_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", "items": []},
    )
    assert ok2 and args2["customer_id"] == uid


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


def test_get_customer_overwrites_wrong_model_customer_id():
    uid = "11111111-2222-3333-4444-555555555555"
    auth = SessionAuthState()
    auth.record_verify_customer_pin_result(f"OK id {uid} end")
    ok, msg, args = auth.prepare_tool_call(
        "get_customer",
        {"customer_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"},
    )
    assert ok and msg == ""
    assert args["customer_id"] == uid
