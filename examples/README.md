# JXON Examples

This directory contains examples of JXON values.
`*.jxon` files are JXON values,
`*.txt` are their annotated hex dumps and
`*.json` are their respective JSON equivalents.

## Simple values 

|File|Hex|Meaning|
|:---|:--|:------|
|[null.jxon](null.jxon) ([dump](null.txt), [json](null.json))|F0|`null`|
|[false.jxon](false.jxon) ([dump](false.txt), [json](false.json))|F1|`false`|
|[true.jxon](true.jxon) ([dump](true.txt), [json](true.json))|F2|`true`|
|[zero.jxon](zero.jxon) ([dump](zero.txt), [json](zero.json))|80|`0`|

## Integers 

|File|Hex|Meaning|
|:---|:--|:------|
|[int_0.jxon](int_0.jxon) ([dump](int_0.txt), [json](int_0.json))|80|`0`|
|[int_1.jxon](int_1.jxon) ([dump](int_1.txt), [json](int_1.json))|81|`1`|
|[int_2.jxon](int_2.jxon) ([dump](int_2.txt), [json](int_2.json))|82|`2`|
|[int_3.jxon](int_3.jxon) ([dump](int_3.txt), [json](int_3.json))|83|`3`|
|[int_4.jxon](int_4.jxon) ([dump](int_4.txt), [json](int_4.json))|84|`4`|
|[int_5.jxon](int_5.jxon) ([dump](int_5.txt), [json](int_5.json))|85|`5`|
|[int_6.jxon](int_6.jxon) ([dump](int_6.txt), [json](int_6.json))|86|`6`|
|[int_7.jxon](int_7.jxon) ([dump](int_7.txt), [json](int_7.json))|87|`7`|
|[int_8.jxon](int_8.jxon) ([dump](int_8.txt), [json](int_8.json))|88|`8`|
|[int_9.jxon](int_9.jxon) ([dump](int_9.txt), [json](int_9.json))|89|`9`|
|[int_10.jxon](int_10.jxon) ([dump](int_10.txt), [json](int_10.json))|8A0A|`10`|
|[int_11.jxon](int_11.jxon) ([dump](int_11.txt), [json](int_11.json))|8A0B|`11`|
|[int_neg_1.jxon](int_neg_1.jxon) ([dump](int_neg_1.txt), [json](int_neg_1.json))|8F|`-1`|
|[int_neg_2.jxon](int_neg_2.jxon) ([dump](int_neg_2.txt), [json](int_neg_2.json))|8AFE|`-2`|
|[int_min8.jxon](int_min8.jxon) ([dump](int_min8.txt), [json](int_min8.json))|8A80|`-128`|
|[int_max8.jxon](int_max8.jxon) ([dump](int_max8.txt), [json](int_max8.json))|8A7F|`127`|
|[int_min16.jxon](int_min16.jxon) ([dump](int_min16.txt), [json](int_min16.json))|8B0080|`-32768`|
|[int_max16.jxon](int_max16.jxon) ([dump](int_max16.txt), [json](int_max16.json))|8BFF7F|`32767`|
|[int_min32.jxon](int_min32.jxon) ([dump](int_min32.txt), [json](int_min32.json))|8C00000080|`-2147483648`|
|[int_max32.jxon](int_max32.jxon) ([dump](int_max32.txt), [json](int_max32.json))|8CFFFFFF7F|`2147483647`|
|[int_min64.jxon](int_min64.jxon) ([dump](int_min64.txt), [json](int_min64.json))|8D0000000000000080|`-9223372036854775808`|
|[int_max64.jxon](int_max64.jxon) ([dump](int_max64.txt), [json](int_max64.json))|8DFFFFFFFFFFFFFF7F|`9223372036854775807`|

## Strings and BLOBs 

|File|Hex|Meaning|
|:---|:--|:------|
|[str_empty.jxon](str_empty.jxon) ([dump](str_empty.txt), [json](str_empty.json))|A000|`""`|
|[str_hello.jxon](str_hello.jxon) ([dump](str_hello.txt), [json](str_hello.json))|A648656C6C6F2100|`"Hello!"`|
|[str_hello_chinese.jxon](str_hello_chinese.jxon) ([dump](str_hello_chinese.txt), [json](str_hello_chinese.json))|A6E4BDA0E5A5BD00|`"你好"` (notice that 6 in `A6` means number of **bytes**, not **characters**)|
|[blob_empty.jxon](blob_empty.jxon) ([dump](blob_empty.txt), [json](blob_empty.json))|90|` `|
|[blob_0123.jxon](blob_0123.jxon) ([dump](blob_0123.txt), [json](blob_0123.json))|9400010203|`00010203`|

## Floats 

|File|Hex|Meaning|
|:---|:--|:------|
|[float_0.jxon](float_0.jxon) ([dump](float_0.txt), [json](float_0.json))|F6|`0.0`|
|[float_1.jxon](float_1.jxon) ([dump](float_1.txt), [json](float_1.json))|F8000000000000F03F|`1.0`|
|[float_nan.jxon](float_nan.jxon) ([dump](float_nan.txt), [json](float_nan.json))|F70000C07F|NaN|
|[float_neg_nan.jxon](float_neg_nan.jxon) ([dump](float_neg_nan.txt), [json](float_neg_nan.json))|F70000C0FF|-NaN|
|[float_inf.jxon](float_inf.jxon) ([dump](float_inf.txt), [json](float_inf.json))|F8000000000000F07F|Infinity|
|[float_neg_inf.jxon](float_neg_inf.jxon) ([dump](float_neg_inf.txt), [json](float_neg_inf.json))|F8000000000000F0FF|-Infinity|
|[float_nan.jxon](float_nan.jxon) ([dump](float_nan.txt), [json](float_nan.json))|F70000C07F|NaN|
|[float_half.jxon](float_half.jxon) ([dump](float_half.txt), [json](float_half.json))|F70000003F|1/2|
|[float_minnorm32.jxon](float_minnorm32.jxon) ([dump](float_minnorm32.txt), [json](float_minnorm32.json))|F700008000|`2^-126` (minimal normalized float)|
|[float_minnorm64.jxon](float_minnorm64.jxon) ([dump](float_minnorm64.txt), [json](float_minnorm64.json))|F80000000000001000|`2^-1022` (minimal normalized double)|

## Structured values 

|File|Hex|Meaning|
|:---|:--|:------|
|[object_empty.jxon](object_empty.jxon) ([dump](object_empty.txt), [json](object_empty.json))|F3F5|`{}`|
|[object.jxon](object.jxon) ([dump](object.txt), [json](object.json))|F3A46B6579310081A...|`{"key1": 1, "key2": "string"}`|
|[array_empty.jxon](array_empty.jxon) ([dump](array_empty.txt), [json](array_empty.json))|F4F5|`[]`|
|[array_123.jxon](array_123.jxon) ([dump](array_123.txt), [json](array_123.json))|F4818283F5|`[1, 2, 3]`|

## Datasets 

|File|Hex|Meaning|
|:---|:--|:------|
|[movies.jxon](movies.jxon) ([dump](movies.txt), [json](movies.json))|F3A66D6F766965730...|List of randomly generated movies|
|[movies_compressed.jxon](movies_compressed.jxon) ([dump](movies_compressed.txt), [json](movies_compressed.json), [protobuf](movies_compressed.pb))|B269640000B574697...|The same list, but keys table is used|
