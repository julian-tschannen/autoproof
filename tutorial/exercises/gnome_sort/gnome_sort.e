note
	description: "Gnome sort algorithm."

class
	GNOME_SORT

feature -- Sorting

	gnome_sort (a: SIMPLE_ARRAY [INTEGER])
			-- Sort array `a' using gnome sort.
			-- https://en.wikipedia.org/wiki/Gnome_sort
		note
			explicit: wrapping
		require
			-- TASK 1: Add specification.
			-- TASK 4: Adapt specification to prevent overflows.
		local
			pos, t: INTEGER
		do
			from
				pos := 2
			invariant
				a.is_wrapped -- Array stays in a consistent state.
				decreases ([]) -- No termination proof.
				
				-- TASK 2: Add loop invariants to verify array accesses.
				-- TASK 3: Add loop invariants to verify postcondition.
			until
				pos > a.count
			loop
				if a[pos] >= a[pos-1] then
					pos := pos + 1
				else
						-- Swap pos and pos-1
					t := a[pos]
					a[pos] := a[pos-1]
					a[pos-1] := t
					if pos > 2 then
						pos := pos - 1
					end
				end
			end
		ensure
			-- TASK 1: Add specification.
		end

feature -- Specification

	is_sorted (s: MML_SEQUENCE [INTEGER]): BOOLEAN
			-- Is `s' sorted?
		note
			status: functional, ghost
		do
			Result := is_part_sorted (s, 1, s.count)
		end

	is_part_sorted (s: MML_SEQUENCE [INTEGER]; lower, upper: INTEGER): BOOLEAN
			-- Is `s' sorted from `lower' to `upper'?
		note
			status: functional, ghost
		require
			lower_in_bounds: lower >= 1
			upper_in_bounds: upper <= s.count
		do
			Result := False -- TASK 1: Add partial sorted implementation.
		end

	is_permutation (s1, s2: MML_SEQUENCE [INTEGER]): BOOLEAN
			-- Are `s1' and `s2' permutations of each other?
		note
			status: functional, ghost
		do
			Result := s1.to_bag ~ s2.to_bag and s1.count = s2.count
		end

end
