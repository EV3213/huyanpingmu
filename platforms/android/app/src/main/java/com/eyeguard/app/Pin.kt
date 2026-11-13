package com.eyeguard.app

import java.security.MessageDigest
import java.security.SecureRandom

/**
 * 家长密码：只保存加盐 SHA-256 摘要，不存明文（与桌面版同一套规则）。
 */
object Pin {

    private val rnd = SecureRandom()

    fun makeSalt(): String {
        val b = ByteArray(8)
        rnd.nextBytes(b)
        return hex(b)
    }

    fun sha256(s: String): String =
        hex(MessageDigest.getInstance("SHA-256").digest(s.toByteArray(Charsets.UTF_8)))

    fun hash(pin: String, salt: String): String = sha256("$salt|$pin")

    /** 4 ~ 8 位数字 */
    fun valid(pin: String): Boolean = pin.length in 4..8 && pin.all { it.isDigit() }

    private fun hex(bytes: ByteArray): String =
        bytes.joinToString("") { String.format("%02x", it.toInt() and 0xff) }
}
