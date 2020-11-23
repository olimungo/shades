# Convert a dotted IPv4 address string into four bytes, with some
# sanity checks
def dotted_ip_to_bytes(ip):
    l = [int(i) for i in ip.split(".")]
    if len(l) != 4 or any(i < 0 or i > 255 for i in l):
        raise ValueError
    return bytes(l)

# Ensure that a name is in the form of a list of encoded blocks of
# bytes, typically starting as a qualified domain name
def check_name(n):
    if isinstance(n, str):
        n = n.split(".")
        if n[-1] == "":
            n = n[:-1]
    n = [i.encode("UTF8") if isinstance(i, str) else i for i in n]
    return n

# Move the offset past the name to which it currently points
def skip_name_at(buf, o):
    while True:
        l = buf[o]
        if l == 0:
            o += 1
            break
        elif (l & 0xC0) == 0xC0:
            o += 2
            break
        else:
            o += l + 1
    return o

# Test if two possibly compressed names are equal
def compare_packed_names(buf, o, packed_name, po=0):
    while packed_name[po] != 0:
        while buf[o] & 0xC0:
            (o,) = unpack_from("!H", buf, o)
            o &= 0x3FFF
        while packed_name[po] & 0xC0:
            (po,) = unpack_from("!H", packed_name, po)
            po &= 0x3FFF
        l1 = buf[o] + 1
        l2 = packed_name[po] + 1
        if l1 != l2 or buf[o : o + l1] != packed_name[po : po + l2]:
            return False
        o += l1
        po += l2
    return buf[o] == 0

# Find the memory size needed to pack a name without compression
def name_packed_len(name):
    return sum(len(i) + 1 for i in name) + 1

# Pack a name into the start of the buffer
def pack_name(buf, name):
    # We don't support writing with name compression, BIWIOMS
    o = 0
    for part in name:
        pl = len(part)
        buf[o] = pl
        buf[o + 1 : o + pl + 1] = part
        o += pl + 1
    buf[o] = 0

# Pack a question into a new array and return it as a memoryview
def pack_question(name, qtype, qclass):
    # Return a pre-packed question as a memoryview
    name = check_name(name)
    name_len = name_packed_len(name)
    buf = bytearray(name_len + 4)
    pack_name(buf, name)
    pack_into("!HH", buf, name_len, qtype, qclass)
    return memoryview(buf)

# Pack an answer into a new array and return it as a memoryview
def pack_answer(name, rtype, rclass, ttl, rdata):
    # Return a pre-packed answer as a memoryview
    name = check_name(name)
    name_len = name_packed_len(name)
    buf = bytearray(name_len + 10 + len(rdata))
    pack_name(buf, name)
    pack_into("!HHIH", buf, name_len, rtype, rclass, ttl, len(rdata))
    buf[name_len + 10 :] = rdata
    return memoryview(buf)

# Advance the offset past the question to which it points
def skip_question(buf, o):
    o = skip_name_at(buf, o)
    return o + 4

# Advance the offset past the answer to which it points
def skip_answer(buf, o):
    o = skip_name_at(buf, o)
    (rdlen,) = unpack_from("!H", buf, o + 8)
    return o + 10 + rdlen

# Test if a questing an answer. Note that this also works for
# comparing a "known answer" in a packet to a local answer. The code
# is asymetric to the extent that the questions my have a type or
# class of ANY
def compare_q_and_a(q_buf, q_offset, a_buf, a_offset=0):
    if not compare_packed_names(q_buf, q_offset, a_buf, a_offset):
        return False
    (q_type, q_class) = unpack_from("!HH", q_buf, skip_name_at(q_buf, q_offset))
    (r_type, r_class) = unpack_from("!HH", a_buf, skip_name_at(a_buf, a_offset))
    if not (q_type == r_type or q_type == _TYPE_ANY):
        return False
    q_class &= _CLASS_MASK
    r_class &= _CLASS_MASK
    return q_class == r_class or q_class == _TYPE_ANY