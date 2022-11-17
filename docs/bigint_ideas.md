There are a plethora of formats for encoding arbitrarily large integers.

[LEB128](https://en.wikipedia.org/wiki/LEB128) is popular and very simple. It is pretty compact (12.5% of memory overhead). Bignum arithmetic can be written for encoded integers.

`LEB128` splits an integer to 7-bits chunks and uses bytes for encoding them. But a modification of this format with 63-bits chunks is more compact (1.5625% overhead) and efficient. `JXON` already has its own commands for small and commonly sized integers, so using such `LEB-POWER-OF-2-TO-63` format seems like a reasonable choice for `JXON`.
