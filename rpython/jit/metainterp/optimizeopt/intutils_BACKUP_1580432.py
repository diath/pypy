import sys
from rpython.rlib.rarithmetic import ovfcheck, LONG_BIT, maxint, is_valid_int, r_uint, intmask
from rpython.rlib.objectmodel import we_are_translated
from rpython.rtyper.lltypesystem import lltype
from rpython.rtyper.lltypesystem.lloperation import llop
from rpython.jit.metainterp.resoperation import rop, ResOperation
from rpython.jit.metainterp.optimizeopt.info import AbstractInfo, INFO_NONNULL,\
     INFO_UNKNOWN, INFO_NULL
from rpython.jit.metainterp.history import ConstInt


MAXINT = maxint
MININT = -maxint - 1

IS_64_BIT = sys.maxint > 2**32

TNUM_UNKNOWN = r_uint(0), r_uint(-1)
TNUM_KNOWN_ZERO = r_uint(0), r_uint(0)
TNUM_KNOWN_BITWISEONE = r_uint(-1), r_uint(0)
TNUM_ONLY_VALUE_DEFAULT = r_uint(0)
TNUM_ONLY_MASK_UNKNOWN = r_uint(-1)
TNUM_ONLY_MASK_DEFAULT = TNUM_ONLY_MASK_UNKNOWN

def next_pow2_m1(n):
    """Calculate next power of 2 greater than n minus one."""
    n |= n >> 1
    n |= n >> 2
    n |= n >> 4
    n |= n >> 8
    n |= n >> 16
    if IS_64_BIT:
        n |= n >> 32
    return n


class IntBound(AbstractInfo):
<<<<<<< HEAD
    """
    Abstract domain representation of an integer,
    approximating via integer bounds and known-bits
    tri-state numbers.
    """
    _attrs_ = ('has_upper', 'has_lower', 'upper', 'lower', 'tvalue', 'tmask')

    def __init__(self, lower=MININT, upper=MAXINT,
                 has_lower=False, has_upper=False,
                 tvalue=TNUM_ONLY_VALUE_DEFAULT,
                 tmask=TNUM_ONLY_MASK_DEFAULT):
        """
        It is recommended to use the indirect constructors
        below instead of this one.
        Instantiates an abstract representation of integer.
        The default parameters set this abstract int to
        contain all integers.
        """

        self.has_lower = has_lower
        self.has_upper = has_upper
=======
    _attrs_ = ('upper', 'lower')

    def __init__(self, lower, upper):
        self.upper = upper
>>>>>>> fix-intutils-ovf-bug
        self.lower = lower
        self.upper = upper

        # known-bit analysis using tristate numbers
        #  see https://arxiv.org/pdf/2105.05398.pdf
        assert is_valid_tnum(tvalue, tmask)
        self.tvalue = tvalue
        self.tmask = tmask         # bit=1 means unknown

        # check for unexpected overflows:
        if not we_are_translated():
            assert type(upper) is not long or is_valid_int(upper)
            assert type(lower) is not long or is_valid_int(lower)

        assert self.knownbits_and_bounds_agree()

    def __repr__(self):
        if self.has_lower:
            l = '%d' % self.lower
        else:
            l = '-Inf'
        if self.has_upper:
            u = '%d' % self.upper
        else:
            u = 'Inf'
        return '(%s <= 0b%s <= %s)' % (l, self.knownbits_string(), u)


    def make_le(self, other):
<<<<<<< HEAD
        """
        Sets the bounds of `self` so that it only
        contains values lower than or equal to the
        values contained in `other`.
        Returns `True` iff the bound was updated.
        (Mutates `self`.)
        """
        if other.has_upper:
            return self.make_le_const(other.upper)
        return False

    def make_le_const(self, value):
        """
        Sets the bounds of `self` so that it
        only contains values lower than or equal
        to `value`.
        Returns `True` iff the bound was updated.
        (Mutates `self`.)
        """
        if not self.has_upper or value < self.upper:
            self.has_upper = True
            self.upper = value
=======
        return self.make_le_const(other.upper)

    def make_le_const(self, other):
        if other < self.upper:
            self.upper = other
>>>>>>> fix-intutils-ovf-bug
            return True
        return False

    def make_lt(self, other):
<<<<<<< HEAD
        """
        Sets the bounds of `self` so that it
        only contains values lower than the values
        contained in `other`.
        Returns `True` iff the bound was updated.
        (Mutates `self`.)
        """
        if other.has_upper:
            return self.make_lt_const(other.upper)
        return False
=======
        return self.make_lt_const(other.upper)
>>>>>>> fix-intutils-ovf-bug

    def make_lt_const(self, value):
        """
        Sets the bounds of `self` so that it
        only contains values lower than `value`.
        Returns `True` iff the bound was updated.
        (Mutates `self`.)
        """
        try:
            value = ovfcheck(value - 1)
        except OverflowError:
            return False
        return self.make_le_const(value)

    def make_ge(self, other):
<<<<<<< HEAD
        """
        Sets the bounds of `self` so that it only
        contains values greater than or equal to the
        values contained in `other`.
        Returns `True` iff the bound was updated.
        (Mutates `self`.)
        """
        if other.has_lower:
            return self.make_ge_const(other.lower)
        return False

    def make_ge_const(self, value):
        """
        Sets the bounds of `self` so that it
        only contains values greater than or equal
        to `value`.
        Returns `True` iff the bound was updated.
        (Mutates `self`.)
        """
        if not self.has_lower or value > self.lower:
            self.has_lower = True
            self.lower = value
            return True
        return False

    def make_gt(self, other):
        """
        Sets the bounds of `self` so that it
        only contains values greater than the values
        contained in `other`.
        Returns `True` iff the bound was updated.
        (Mutates `self`.)
        """
        if other.has_lower:
            return self.make_gt_const(other.lower)
        return False

    def make_gt_const(self, value):
        """
        Sets the bounds of `self` so that it
        only contains values greater than `value`.
        Returns `True` iff the bound was updated.
        (Mutates `self`.)
        """
        try:
            value = ovfcheck(value + 1)
        except OverflowError:
            return False
        return self.make_ge_const(value)

    def make_eq_const(self, intval):
        """
        Sets the properties of this abstract integer
        so that it is constant and equals `intval`.
        (Mutates `self`.)
        """
        self.has_upper = True
        self.has_lower = True
        self.upper = intval
        self.lower = intval
        self.tvalue = r_uint(intval)
        self.tmask = r_uint(0)

    def is_constant_by_bounds(self):
        """ for internal use only! """
        return self.is_bounded() and (self.lower == self.upper)

    def is_constant_by_knownbits(self):
        """ for internal use only! """
        return self.tmask == 0

    def is_constant(self):
        """
        Returns `True` iff this abstract integer
        does contain only one (1) concrete integer.
        """
        return self.is_constant_by_bounds() or \
               self.is_constant_by_knownbits()
=======
        return self.make_ge_const(other.lower)

    def make_ge_const(self, other):
        if other > self.lower:
            self.lower = other
            return True
        return False

    def make_gt_const(self, other):
        try:
            other = ovfcheck(other + 1)
        except OverflowError:
            return False
        return self.make_ge_const(other)

    def make_eq_const(self, intval):
        self.upper = intval
        self.lower = intval

    def make_ne_const(self, intval):
        if self.lower < intval == self.upper:
            self.upper -= 1
            return True
        if self.lower == intval < self.upper:
            self.lower += 1
            return True
        return False

    def make_gt(self, other):
        return self.make_gt_const(other.lower)

    def is_constant(self):
        return self.lower == self.upper
>>>>>>> fix-intutils-ovf-bug

    def get_constant_int(self):
        """
        Returns the only integer contained in this
        abstract integer, asserting that it
        `is_constant()`.
        """
        assert self.is_constant()
        if self.is_constant_by_bounds():
            return self.lower
        else:  # is_constant_by_knownbits
            return intmask(self.tvalue)

<<<<<<< HEAD
    def is_bounded(self):
        """
        Returns `True` iff this abstract integer
        has both, a lower and an upper bound.
        """
        return self.has_lower and self.has_upper

    def equals(self, value):
        """
        Returns `True` iff this abstract integer
        contains only one (1) integer that does
        equal `value`.
        """
        if not self.is_constant():
            return False
        if self.is_constant_by_bounds():
            return self.lower == value
        else:
            return r_uint(value) == self.tvalue

    def known_lt_const(self, value):
        """
        Returns `True` iff each number contained
        in this abstract integer is lower than
        `value`.
        """
        if self.has_upper:
            #maxest = self.upper
            #import pdb; pdb.set_trace()
            maxest = self.get_maximum_estimation_signed()
            return maxest < value
        return False

    def known_le_const(self, value):
        """
        Returns `True` iff each number contained
        in this abstract integer is lower than
        or equal to `value`.
        """
        if self.has_upper:
            #maxest = self.upper
            #import pdb; pdb.set_trace()
            maxest = self.get_maximum_estimation_signed()
            return maxest <= value
        return False

    def known_gt_const(self, value):
        """
        Returns `True` iff each number contained
        in this abstract integer is greater than
        `value`.
        """
        if self.has_lower:
            #minest = self.lower
            #import pdb; pdb.set_trace()
            minest = self.get_minimum_estimation_signed()
            return minest > value
        return False

    def known_ge_const(self, value):
        """
        Returns `True` iff each number contained
        in this abstract integer is greater than
        equal to `value`.
        """
        if self.has_upper:
            #minest = self.lower
            #import pdb; pdb.set_trace()
            minest = self.get_minimum_estimation_signed()
            return minest >= value
        return False

    def known_lt(self, other):
        """
        Returns `True` iff each number contained
        in this abstract integer is lower than
        each integer contained in `other`.
        """
        if other.has_lower:
            #o_minest = other.lower
            #import pdb; pdb.set_trace()
            o_minest = other.get_minimum_estimation_signed()
            return self.known_lt_const(o_minest)
        return False

    def known_le(self, other):
        """
        Returns `True` iff each number contained
        in this abstract integer is lower than
        or equal to each integer contained in
        `other`.
        """
        if other.has_lower:
            #o_minest = other.lower
            #import pdb; pdb.set_trace()
            o_minest = other.get_minimum_estimation_signed()
            return self.known_le_const(o_minest)
        return False
=======
    def equal(self, value):
        if not self.is_constant():
            return False
        return self.lower == value

    def known_lt_const(self, other):
        return self.upper < other

    def known_le_const(self, other):
        return self.upper <= other

    def known_gt_const(self, other):
        return self.lower > other

    def known_ge_const(self, other):
        return self.upper >= other

    def known_lt(self, other):
        return self.known_lt_const(other.lower)

    def known_le(self, other):
        return self.known_le_const(other.lower)
>>>>>>> fix-intutils-ovf-bug

    def known_gt(self, other):
        """
        Returns `True` iff each number contained
        in this abstract integer is greater than
        each integer contained in `other`.
        """
        return other.known_lt(self)

    def known_ge(self, other):
        """
        Returns `True` iff each number contained
        in this abstract integer is greater than
        or equal to each integer contained in
        `other`.
        """
        return other.known_le(self)

    def known_nonnegative(self):
<<<<<<< HEAD
        """
        Returns `True` if this abstract integer
        only contains numbers greater than or
        equal to `0` (zero).
        """
        #return self.has_lower and 0 <= self.lower
        return 0 <= self.get_minimum_estimation_signed()

    def known_nonnegative_by_bounds(self):
        """ for internal use only! """
        # Returns `True` if this abstract integer
        # only contains numbers greater than or
        # equal to `0` (zero), IGNORING KNOWNBITS.
        if not self.has_lower:
            return False
        else:
            minest = self.get_minimum_estimation_signed()
            return 0 <= minest

    def get_minimum_signed_by_knownbits(self):
        """ for internal use only! """
        return intmask(self.tvalue | msbonly(self.tmask))

    def get_maximum_signed_by_knownbits(self):
        """ for internal use only! """
        unsigned_mask = self.tmask & ~msbonly(self.tmask)
        return intmask(self.tvalue | unsigned_mask)

    def get_minimum_estimation_signed(self):
        """
        Returns an estimated lower bound for
        the numbers contained in this
        abstract integer.
        It is not guaranteed that this value
        is actually an element of the
        concrete value set!
        """
        # Unnecessary to unmask, because by convention
        #   mask[i] => ~value[i]
        ret_knownbits = self.get_minimum_signed_by_knownbits()
        ret_bounds = self.lower
        if self.has_lower:
            return max(ret_knownbits, ret_bounds)
        else:
            return ret_knownbits

    def get_maximum_estimation_signed(self):
        """
        Returns an estimated upper bound for
        the numbers contained in this
        abstract integer.
        It is not guaranteed that this value
        is actually an element of the
        concrete value set!
        """
        ret_knownbits = self.get_maximum_signed_by_knownbits()
        ret_bounds = self.upper
        if self.has_upper:
            return min(ret_knownbits, ret_bounds)
        else:
            return ret_knownbits
=======
        return 0 <= self.lower
>>>>>>> fix-intutils-ovf-bug

    def intersect(self, other):
        """
        Mutates `self` so that it contains
        integers that are contained in `self`
        and `other`, and only those.
        Basically intersection of sets.
        Throws errors if `self` and `other`
        "disagree", meaning the result would
        contain 0 (zero) any integers.
        """

        r = False
<<<<<<< HEAD
        if other.has_lower:
            if self.make_ge_const(other.lower):
                r = True
        if other.has_upper:
            if self.make_le_const(other.upper):
                r = True

        # tnum stuff.
        union_val = self.tvalue | other.tvalue
        intersect_masks = self.tmask & other.tmask
        union_masks = self.tmask | other.tmask
        # we assert agreement, e.g. that self and other don't contradict
        unmasked_self = unmask_zero(self.tvalue, union_masks)
        unmasked_other = unmask_zero(other.tvalue, union_masks)
        assert unmasked_self == unmasked_other
        # calculate intersect value and mask
        if self.tmask != intersect_masks:
            self.tvalue = unmask_zero(union_val, intersect_masks)
            self.tmask = intersect_masks
            r = True

        # we also assert agreement between knownbits and bounds
        assert self.knownbits_and_bounds_agree()

=======
        if self.make_ge_const(other.lower):
            r = True
        if self.make_le_const(other.upper):
            r = True
>>>>>>> fix-intutils-ovf-bug
        return r

    def intersect_const(self, lower, upper):
        """
        Mutates `self` so that it contains
        integers that are contained in `self`
        and the range [`lower`, `upper`],
        and only those.
        Basically intersection of sets.
        Does only affect the bounds, so if
        possible the use of the `intersect`
        function is recommended instead.
        """
        r = self.make_ge_const(lower)
        if self.make_le_const(upper):
            r = True

        return r

<<<<<<< HEAD
    def add(self, offset):
        """
        Adds `offset` to this abstract int
        and returns the result.
        (Does not mutate `self`.)
        """
        return self.add_bound(ConstIntBound(offset))

    def mul(self, value):
        """
        Multiplies this abstract int with the
        given `value` and returns the result.
        (Does not mutate `self`.)
        """
        return self.mul_bound(ConstIntBound(value))

    def add_bound(self, other):
        """
        Adds the `other` abstract integer to
        `self` and returns the result.
        (Does not mutate `self`.)
        """

        #import pdb; pdb.set_trace()

        res = self.clone()

        sum_values = self.tvalue + other.tvalue
        sum_masks = self.tmask + other.tmask
        all_carries = sum_values + sum_masks
        val_carries = all_carries ^ sum_values
        res.tmask = self.tmask | other.tmask | val_carries
        res.tvalue = unmask_zero(sum_values, res.tmask)

        # TODO: Can this be done better with minimum/maximum?
        if (~res.has_upper and ~other.known_le(ConstIntBound(0))) \
           or (~res.has_lower and ~other.known_ge(ConstIntBound(0))):
            res.has_lower = False
            res.has_upper = False
            return res

        if other.has_upper and res.has_upper:
            try:
                res.upper = ovfcheck(res.upper + other.upper)
            except OverflowError:
                res.has_lower = False
                res.has_upper = False
                return res
        else:
            res.has_upper = False
        if other.has_lower and res.has_lower:
            try:
                res.lower = ovfcheck(res.lower + other.lower)
            except OverflowError:
                res.has_lower = False
                res.has_upper = False
                return res
        else:
            res.has_lower = False

        return res

    def sub_bound(self, other):
        """
        Subtracts the `other` abstract
        integer from `self` and returns the
        result.
        (Does not mutate `self`.)
        """
        res = self.add_bound(other.neg_bound())
        return res

    def mul_bound(self, other):
        """
        Multiplies the `other` abstract
        integer with `self` and returns the
        result.
        (Does not mutate `self`.)
        """
        if self.has_upper and self.has_lower and \
           other.has_upper and other.has_lower:
            try:
                vals = (ovfcheck(self.upper * other.upper),
                        ovfcheck(self.upper * other.lower),
                        ovfcheck(self.lower * other.upper),
                        ovfcheck(self.lower * other.lower))
                return IntLowerUpperBound(min4(vals), max4(vals))
            except OverflowError:
                return IntUnbounded()
        else:
=======
    def add_bound(self, other):
        """ add two bounds. must be correct even in the presence of possible
        overflows. """
        try:
            lower = ovfcheck(self.lower + other.lower)
        except OverflowError:
            return IntUnbounded()
        try:
            upper = ovfcheck(self.upper + other.upper)
        except OverflowError:
            return IntUnbounded()
        return IntBound(lower, upper)

    def add_bound_cannot_overflow(self, other):
        """ returns True if self + other can never overflow """
        try:
            ovfcheck(self.upper + other.upper)
            ovfcheck(self.lower + other.lower)
        except OverflowError:
            return False
        return True

    def add_bound_no_overflow(self, other):
        """ return the bound that self + other must have, if no overflow occured,
        eg after an int_add_ovf(...), guard_no_overflow() """
        lower = MININT
        try:
            lower = ovfcheck(self.lower + other.lower)
        except OverflowError:
            pass
        upper = MAXINT
        try:
            upper = ovfcheck(self.upper + other.upper)
        except OverflowError:
            pass
        return IntBound(lower, upper)

    def sub_bound(self, other):
        try:
            lower = ovfcheck(self.lower - other.upper)
        except OverflowError:
            return IntUnbounded()
        try:
            upper = ovfcheck(self.upper - other.lower)
        except OverflowError:
            return IntUnbounded()
        return IntBound(lower, upper)

    def sub_bound_cannot_overflow(self, other):
        try:
            ovfcheck(self.lower - other.upper)
            ovfcheck(self.upper - other.lower)
        except OverflowError:
            return False
        return True

    def sub_bound_no_overflow(self, other):
        lower = MININT
        try:
            lower = ovfcheck(self.lower - other.upper)
        except OverflowError:
            pass
        upper = MAXINT
        try:
            upper = ovfcheck(self.upper - other.lower)
        except OverflowError:
            pass
        return IntBound(lower, upper)

    def mul_bound(self, other):
        try:
            vals = (ovfcheck(self.upper * other.upper),
                    ovfcheck(self.upper * other.lower),
                    ovfcheck(self.lower * other.upper),
                    ovfcheck(self.lower * other.lower))
            return IntBound(min4(vals), max4(vals))
        except OverflowError:
>>>>>>> fix-intutils-ovf-bug
            return IntUnbounded()
    mul_bound_no_overflow = mul_bound # can be improved

    def mul_bound_cannot_overflow(self, other):
        try:
            ovfcheck(self.upper * other.upper)
            ovfcheck(self.upper * other.lower)
            ovfcheck(self.lower * other.upper)
            ovfcheck(self.lower * other.lower)
        except OverflowError:
            return False
        return True

    def py_div_bound(self, other):
<<<<<<< HEAD
        """
        Divides this abstract integer by the
        `other` abstract integer and returns
        the result.
        (Does not mutate `self`.)
        """
        if self.has_upper and self.has_lower and \
           other.has_upper and other.has_lower and \
           not other.contains(0):
=======
        if not other.contains(0):
>>>>>>> fix-intutils-ovf-bug
            try:
                # this gives the bounds for 'int_py_div', so use the
                # Python-style handling of negative numbers and not
                # the C-style one
                vals = (ovfcheck(self.upper / other.upper),
                        ovfcheck(self.upper / other.lower),
                        ovfcheck(self.lower / other.upper),
                        ovfcheck(self.lower / other.lower))
                return IntLowerUpperBound(min4(vals), max4(vals))
            except OverflowError:
                pass
        return IntUnbounded()

    def mod_bound(self, other):
        """
        Calculates the mod of this abstract
        integer by the `other` abstract
        integer and returns the result.
        (Does not mutate `self`.)
        """
        r = IntUnbounded()
        if other.is_constant():
            val = other.get_constant_int()
            if val >= 0:        # with Python's modulo:  0 <= (x % pos) < pos
                r.make_ge_const(0)
                r.make_lt_const(val)
            else:               # with Python's modulo:  neg < (x % neg) <= 0
                r.make_gt_const(val)
                r.make_le_const(0)
        return r

    def lshift_bound(self, other):
<<<<<<< HEAD
        """
        Shifts this abstract integer `other`
        bits to the left, where `other` is
        another abstract integer.
        (Does not mutate `self`.)
        """

        tvalue, tmask = TNUM_UNKNOWN
        if other.is_constant():
            c_other = other.get_constant_int()
            if c_other >= LONG_BIT:
                tvalue, tmask = TNUM_KNOWN_ZERO
            elif c_other >= 0:
                tvalue = self.tvalue << r_uint(c_other)
                tmask = self.tmask << r_uint(c_other)
            # else: bits are unknown because arguments invalid

        if self.is_bounded() and other.is_bounded() and \
           other.known_nonnegative_by_bounds() and \
=======
        if other.known_nonnegative() and \
>>>>>>> fix-intutils-ovf-bug
           other.known_lt_const(LONG_BIT):
            try:
                vals = (ovfcheck(self.upper << other.upper),
                        ovfcheck(self.upper << other.lower),
                        ovfcheck(self.lower << other.upper),
                        ovfcheck(self.lower << other.lower))
                return IntLowerUpperBoundKnownbits(min4(vals), max4(vals),
                                                   tvalue, tmask)
            except (OverflowError, ValueError):
                pass
<<<<<<< HEAD

        return IntBoundKnownbits(tvalue, tmask)

    def rshift_bound(self, other):
        """
        Shifts this abstract integer `other`
        bits to the right, where `other` is
        another abstract integer, and extends
        its sign.
        (Does not mutate `self`.)
        """

        # this seems to always be the signed variant..?
        tvalue, tmask = TNUM_UNKNOWN
        if other.is_constant():
            c_other = other.get_constant_int()
            if c_other >= LONG_BIT:
                # shift value out to the right, but do sign extend
                if msbonly(self.tmask): # sign-extend mask
                    tvalue, tmask = TNUM_UNKNOWN
                elif msbonly(self.tvalue): # sign-extend value
                    tvalue, tmask = TNUM_KNOWN_BITWISEONE
                else: # sign is 0 on both
                    tvalue, tmask = TNUM_KNOWN_ZERO
            elif c_other >= 0:
                # we leverage native sign extension logic
                tvalue = r_uint(intmask(self.tvalue) >> c_other)
                tmask = r_uint(intmask(self.tmask) >> c_other)
            # else: bits are unknown because arguments invalid

        if self.is_bounded() and other.is_bounded() and \
           other.known_nonnegative_by_bounds() and \
=======
        return IntUnbounded()

    def lshift_bound_cannot_overflow(self, other):
        if other.known_nonnegative() and \
           other.known_lt_const(LONG_BIT):
            try:
                ovfcheck(self.upper << other.upper)
                ovfcheck(self.upper << other.lower)
                ovfcheck(self.lower << other.upper)
                ovfcheck(self.lower << other.lower)
                return True
            except (OverflowError, ValueError):
                pass
        return False


    def rshift_bound(self, other):
        if other.known_nonnegative() and \
>>>>>>> fix-intutils-ovf-bug
           other.known_lt_const(LONG_BIT):
            vals = (self.upper >> other.upper,
                    self.upper >> other.lower,
                    self.lower >> other.upper,
                    self.lower >> other.lower)
            return IntLowerUpperBoundKnownbits(min4(vals), max4(vals),
                                               tvalue, tmask)
        else:
            return IntBoundKnownbits(tvalue, tmask)

    def urshift_bound(self, other):
        """
        Shifts this abstract integer `other`
        bits to the right, where `other` is
        another abstract integer, *without*
        extending its sign.
        (Does not mutate `self`.)
        """

        # this seems to always be the signed variant..?
        tvalue, tmask = TNUM_UNKNOWN
        if other.is_constant():
            c_other = other.get_constant_int()
            if c_other >= LONG_BIT:
                # no sign to extend, we get constant 0
                tvalue, tmask = TNUM_KNOWN_ZERO
            elif c_other >= 0:
                tvalue = self.tvalue >> r_uint(c_other)
                tmask = self.tmask >> r_uint(c_other)
            # else: bits are unknown because arguments invalid

        # we don't do bounds on unsigned
        return IntBoundKnownbits(tvalue, tmask)

    def and_bound(self, other):
        """
        Performs bit-wise AND of this
        abstract integer and the `other`,
        returning its result.
        (Does not mutate `self`.)
        """

        pos1 = self.known_nonnegative_by_bounds()
        pos2 = other.known_nonnegative_by_bounds()
        r = IntUnbounded()
        if pos1 or pos2:
            r.make_ge_const(0)
        if pos1:
            r.make_le(self)
        if pos2:
            r.make_le(other)

        self_pmask = self.tvalue | self.tmask
        other_pmask = other.tvalue | other.tmask
        and_vals = self.tvalue & other.tvalue
        r.tvalue = and_vals
        r.tmask = self_pmask & other_pmask & ~and_vals

        return r

    def or_bound(self, other):
        """
        Performs bit-wise OR of this
        abstract integer and the `other`,
        returning its result.
        (Does not mutate `self`.)
        """

        r = IntUnbounded()
<<<<<<< HEAD

        if self.known_nonnegative_by_bounds() and \
                other.known_nonnegative_by_bounds():
            if self.has_upper and other.has_upper:
                mostsignificant = self.upper | other.upper
                r.intersect(IntLowerUpperBound(0, next_pow2_m1(mostsignificant)))
            else:
                r.make_ge_const(0)

        union_vals = self.tvalue | other.tvalue
        union_masks = self.tmask | other.tmask
        r.tvalue = union_vals
        r.tmask = union_masks & ~union_vals

        return r

    def xor_bound(self, other):
        """
        Performs bit-wise XOR of this
        abstract integer and the `other`,
        returning its result.
        (Does not mutate `self`.)
        """

        r = IntUnbounded()

        if self.known_nonnegative_by_bounds() and \
                other.known_nonnegative_by_bounds():
            if self.has_upper and other.has_upper:
                mostsignificant = self.upper | other.upper
                r.intersect(IntLowerUpperBound(0, next_pow2_m1(mostsignificant)))
            else:
                r.make_ge_const(0)

        xor_vals = self.tvalue ^ other.tvalue
        union_masks = self.tmask | other.tmask
        r.tvalue = unmask_zero(xor_vals, union_masks)
        r.tmask = union_masks

        return r

    def invert_bound(self):
        """
        Performs bit-wise NOT on this
        abstract integer returning its
        result.
        (Does not mutate `self`.)
        """

        res = self.clone()

        res.has_upper = False
        if self.has_lower:
            res.upper = ~self.lower
            res.has_upper = True
        res.has_lower = False
        if self.has_upper:
            res.lower = ~self.upper
            res.has_lower = True

        res.tvalue = unmask_zero(~res.tvalue, res.tmask)

        return res

    def neg_bound(self):
        """
        Arithmetically negates this abstract
        integer and returns the result.
        (Does not mutate `self`.)
        """
        res = self.invert_bound()
        res = res.add(1)
        return res
=======
        if self.known_nonnegative() and \
                other.known_nonnegative():
            mostsignificant = self.upper | other.upper
            r.intersect(IntBound(0, next_pow2_m1(mostsignificant)))
        return r

    def invert_bound(self):
        upper = ~self.lower
        lower = ~self.upper
        return IntBound(lower, upper)

    def neg_bound(self):
        try:
            upper = ovfcheck(-self.lower)
        except OverflowError:
            return IntUnbounded()
        try:
            lower = ovfcheck(-self.upper)
        except OverflowError:
            return IntUnbounded()
        return IntBound(lower, upper)
>>>>>>> fix-intutils-ovf-bug

    def contains(self, val):
        """
        Returns `True` iff this abstract
        integer contains the given `val`ue.
        """

        if not we_are_translated():
            assert not isinstance(val, long)
        if not isinstance(val, int):
            if (self.lower == MININT and self.upper == MAXINT):
                return True # workaround for address as int
        if val < self.lower:
            return False
        if val > self.upper:
            return False

        u_vself = unmask_zero(self.tvalue, self.tmask)
        u_value = unmask_zero(r_uint(val), self.tmask)
        if u_vself != u_value:
            return False

        return True

    def contains_bound(self, other):
        """
        Returns `True` iff this abstract
        integers contains each number that
        is contained in the `other` one.
        """

        assert isinstance(other, IntBound)
        if not self.contains(other.lower):
            return False
        if not self.contains(other.upper):
            return False

        union_masks = self.tmask | other.tmask
        if unmask_zero(self.tvalue, self.tmask) != unmask_zero(other.tvalue, union_masks):
            return False

        return True

<<<<<<< HEAD
    def clone(self):
        """
        Returns an exact copy of this
        abstract integer.
        """
        res = IntBound(self.lower, self.upper,
                       self.has_lower, self.has_upper,
                       self.tvalue, self.tmask)
=======
    def __repr__(self):
        return '%d <= x <= %u' % (self.lower, self.upper)

    def clone(self):
        res = IntBound(self.lower, self.upper)
>>>>>>> fix-intutils-ovf-bug
        return res

    def make_guards(self, box, guards, optimizer):
        """
        Generates guards from the information
        we have about the numbers this
        abstract integer contains.
        """
        if self.is_constant():
            guards.append(ResOperation(rop.GUARD_VALUE,
                                       [box, ConstInt(self.upper)]))
            return
        if self.lower > MININT:
            bound = self.lower
            op = ResOperation(rop.INT_GE, [box, ConstInt(bound)])
            guards.append(op)
            op = ResOperation(rop.GUARD_TRUE, [op])
            guards.append(op)
        if self.upper < MAXINT:
            bound = self.upper
            op = ResOperation(rop.INT_LE, [box, ConstInt(bound)])
            guards.append(op)
            op = ResOperation(rop.GUARD_TRUE, [op])
            guards.append(op)

    def is_bool(self):
<<<<<<< HEAD
        """
        Returns `True` iff the properties
        of this abstract integer allow it to
        represent a conventional boolean
        value.
        """
        return (self.is_bounded() and self.known_nonnegative() and
=======
        return (self.known_nonnegative() and
>>>>>>> fix-intutils-ovf-bug
                self.known_le_const(1))

    def make_bool(self):
        """
        Mutates this abstract integer so that
        it does represent a conventional
        boolean value.
        (Mutates `self`.)
        """
        self.intersect(IntLowerUpperBound(0, 1))

    def getconst(self):
        """
        Returns an abstract integer that
        equals the value of this abstract
        integer if it is constant, otherwise
        throws an Exception.
        """
        if not self.is_constant():
            raise Exception("not a constant")
        return ConstInt(self.get_constant_int())

    def getnullness(self):
        """
        Returns information about whether
        this this abstract integer is known
        to be zero or not to be zero.
        """
        if self.known_gt_const(0) or \
           self.known_lt_const(0) or \
           self.tvalue != 0:
            return INFO_NONNULL
        if self.known_nonnegative() and \
           self.known_le_const(0):
            return INFO_NULL
        return INFO_UNKNOWN

    def and_bound_backwards(self, other, result_int):
        """
        result_int == int_and(self, other)
        We want to refine our knowledge about self
        using this information

        regular &:
                  other
         &  0   1   ?
         0  0   0   0
         1  0   1   ?
         ?  0   ?   ?   <- result
        self

        backwards & (this one):
                  other
            0   1   ?
         0  ?   0   ?
         1  X?  1   ?
         ?  ?   ?   ?   <- self
        result

        If the knownbits of self and result are inconsistent,
        the values of result are used (this must not happen
        in practice and will be caught by an assert in intersect())
        """

        tvalue = self.tvalue
        tmask = self.tmask
        tvalue &= ~other.tvalue | other.tmask
        tvalue |= r_uint(result_int) & other.tvalue
        tmask &= ~other.tvalue | other.tmask
        return IntBoundKnownbits(tvalue, tmask)

    def or_bound_backwards(self, other, result_int):
        """
        result_int == int_or(self, other)
        We want to refine our knowledge about self
        using this information

        regular |:
                  other
         &  0   1   ?
         0  0   1   ?
         1  1   1   ?
         ?  ?   ?   ?   <- result
        self

        backwards | (this one):
                  other
            0   1   ?
         0  0   X?  X0
         1  1   ?   ?
         ?  ?   ?   ?   <- self (where X=invalid)
        result

        For every X just go ?.
        If the knownbits of self and result are inconsistent,
        the values of result are used (this must not happen
        in practice and will be caught by an assert in intersect())
        """
        pass

    def urshift_bound_backwards(self, other, result):
        """
        Performs a `urshift` backwards on
        `result`. Basically left-shifts
        `result` by `other` binary digits,
        filling the lower part with ?, and
        returns the result.
        """
        if not other.is_constant():
            return IntUnbounded()
        c_other = other.get_constant_int()
        tvalue, tmask = TNUM_UNKNOWN
        if 0 <= c_other < LONG_BIT:
            tvalue = result.tvalue << r_uint(c_other)
            tmask = result.tmask << r_uint(c_other)
            # shift ? in from the right,
            # but we know some bits from `self`
            s_tmask = (r_uint(1) << r_uint(c_other)) - 1
            s_tvalue = s_tmask & self.tvalue
            s_tmask &= self.tmask
            tvalue |= s_tvalue
            tmask |= s_tmask
        # ignore bounds # TODO: bounds
        return IntBoundKnownbits(tvalue, tmask)

    def rshift_bound_backwards(self, other, result):
        # left shift is the reverse function of
        # both urshift and rshift.
        return self.urshift_bound_backwards(other, result)


    """def internal_intersect():
        # synchronizes bounds and knownbits values
        # this does most likely not cover edge cases like overflows
        def sync_ktb_min():
            # transcribes from knownbits to bounds minimum
            t_minimum = unmask_zero(self.tvalue, self.tmask)
            # set negative iff msb unknown or 1
            t_minimum |= msbonly(self.tvalue) | msbonly(self.tmask)
            self.lower = t_minimum
        def sync_ktb_max():
            # transcribes from knownbits to bounds maximum
            t_maximum = unmask_one(self.tvalue, self.tmask)
            # set positive iff msb unknown or 0
            t_maximum &= ~(~msbonly(self.tvalue) | msbonly(self.tmask))
            self.upper = t_maximum
        def sync_btk():
            # transcribes from bounds to knownbits"""

    def knownbits_and_bounds_agree(self):
        """
        Returns `True` iff the span of
        knownbits and the span of the bounds
        have a non-empty intersection.
        That does not guarantee for the
        actual concrete value set to contain
        any values!
        """
        if self.has_lower:
            max_knownbits = self.get_maximum_signed_by_knownbits()
            if not max_knownbits >= self.lower:
                return False
        if self.has_upper:
            min_knownbits = self.get_minimum_signed_by_knownbits()
            if not min_knownbits <= self.upper:
                return False
        return True

    def knownbits_string(self, unk_sym = '?'):
        """
        Returns a beautiful string
        representation about the knownbits
        part of this abstract integer.
        You can give any symbol or string
        for the "unknown bits"
        (default: '?'), the other digits are
        written as '1' and '0'.
        """
        results = []
        for bit in range(LONG_BIT):
            if self.tmask & (1 << bit):
                results.append(unk_sym)
            else:
                results.append(str((self.tvalue >> bit) & 1))
        results.reverse()
        return "".join(results)


def IntLowerUpperBound(lower, upper):
    b = IntBound(lower=lower,
                 upper=upper,
                 has_lower=True,
                 has_upper=True)
    """
    Constructs an abstract integer that is
    greater than or equal to `lower` and
    lower than or equal to `upper`, e.g.
    it is bound by `lower` and `upper`.
    """
    return b

def IntUpperBound(upper):
<<<<<<< HEAD
    b = IntBound(lower=0,
                 upper=upper,
                 has_lower=False,
                 has_upper=True)
    """
    Constructs an abstract integer that is
    lower than or equal to `upper`, e.g.
    it is bound by `upper`.
    """
    return b

def IntLowerBound(lower):
    b = IntBound(lower=lower,
                 upper=0,
                 has_lower=True,
                 has_upper=False)
    """
    Constructs an abstract integer that is
    greater than or equal to `lower`, e.g.
    it is bound by `lower`.
    """
    return b

def IntUnbounded():
    """
    Constructs an abstract integer that is
    completely unknown (e.g. it contains
    every integer).
    """
    b = IntBound()
    return b
=======
    b = IntBound(lower=MININT, upper=upper)
    return b

def IntLowerBound(lower):
    b = IntBound(upper=MAXINT, lower=lower)
    return b

def IntUnbounded():
    return IntBound(MININT, MAXINT)
>>>>>>> fix-intutils-ovf-bug

def ConstIntBound(value):
    """
    Constructs an abstract integer that
    represents a constant (a completely
    known integer).
    """
    # this one does NOT require a r_uint for `value`.
    assert not isinstance(value, r_uint)
    tvalue = value
    tmask = 0
    bvalue = value
    if not isinstance(value, int):
        # workaround for AddressAsInt / symbolic ints
        # by CF
        tvalue = 0
        tmask = -1
        bvalue = 0
    b = IntBound(lower=bvalue,
                 upper=bvalue,
                 has_lower=True,
                 has_upper=True,
                 tvalue=r_uint(tvalue),
                 tmask=r_uint(tmask))
    return b

def IntBoundKnownbits(value, mask, do_unmask=False):
    """
    Constructs an abstract integer where the
    bits determined by `value` and `mask` are
    (un-)known.
    Requires an `r_uint` for `value` and
    `mask`!
    """
    # this one does require a r_uint for `value` and `mask`.
    assert isinstance(value, r_uint) and isinstance(mask, r_uint)
    if do_unmask:
        value = unmask_zero(value, mask)
    b = IntBound(lower=0,
                 upper=0,
                 has_lower=False,
                 has_upper=False,
                 tvalue=value,
                 tmask=mask)
    return b

def IntLowerUpperBoundKnownbits(lower, upper, value, mask, do_unmask=False):
    """
    Constructs an abstract integer that
    is bound by `lower` and `upper`, where
    the bits determined by `value` and `mask`
    are (un-)known.
    Requires an `r_uint` for `value` and
    `mask`!
    """
    # this one does require a r_uint for `value` and `mask`.
    assert isinstance(value, r_uint) and isinstance(mask, r_uint)
    if do_unmask:
        value = unmask_zero(value, mask)
    b = IntBound(lower=lower,
                 upper=upper,
                 has_lower=True,
                 has_upper=True,
                 tvalue=value,
                 tmask=mask)
    return b

def unmask_zero(value, mask):
    """
    Sets all unknowns determined by
    `mask` in `value` bit-wise to 0 (zero)
    and returns the result.
    """
    return value & ~mask

def unmask_one(value, mask):
    """
    Sets all unknowns determined by
    `mask` in `value` bit-wise to 1 (one)
    and returns the result.
    """
    return value | mask

def min4(t):
    """
    Returns the minimum of the values in
    the quadruplet t.
    """
    return min(min(t[0], t[1]), min(t[2], t[3]))

def max4(t):
    """
    Returns the maximum of the values in
    the quadruplet t.
    """
    return max(max(t[0], t[1]), max(t[2], t[3]))

def msbonly(v):
    """
    Returns `v` with all bits except the
    most significant bit set to 0 (zero).
    """
    return v & (1 << (LONG_BIT-1))

def is_valid_tnum(tvalue, tmask):
    """
    Returns `True` iff `tvalue` and `tmask`
    would be valid tri-state number fields
    of an abstract integer, meeting all
    conventions and requirements.
    """
    if not isinstance(tvalue, r_uint):
        return False
    if not isinstance(tmask, r_uint):
        return False
    return 0 == (r_uint(tvalue) & r_uint(tmask))

def lowest_set_bit_only(val_uint):
    """
    Returns an val_int, but with all bits
    deleted but the lowest one that was set.
    """
    assert isinstance(val_uint, r_uint)
    working_val = ~val_uint
    increased_val = working_val + 1
    result = (working_val^increased_val) & ~working_val
    return result