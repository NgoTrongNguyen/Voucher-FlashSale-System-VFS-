-- KEYS:
--   KEYS[1]: "voucher:{voucher_id}:inventory"
--   KEYS[2]: "user:{user_id}:lock"
-- 
-- ARGS:
--   ARGS[1]: cooldown_seconds (mặc định 1 giây)
--
-- RETURN:
--   [1, "success"] nếu thành công (trừ kho 1 cái)
--   [0, "error_message"] nếu thất bại

local voucher_key = KEYS[1]
local user_lock_key = KEYS[2]
local cooldown = tonumber(ARGS[1]) or 1

if redis