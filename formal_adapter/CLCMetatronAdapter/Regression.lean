namespace CLCMetatronAdapter

def booleanFlip (b : Bool) : Bool := !b

def booleanObserve (b : Bool) : Bool := b

theorem boolean_flip_not_continuation_neutral :
    ¬ (∀ b : Bool, booleanObserve (booleanFlip b) = booleanObserve b) := by
  intro h
  have hfalse := h false
  simp [booleanObserve, booleanFlip] at hfalse

end CLCMetatronAdapter
