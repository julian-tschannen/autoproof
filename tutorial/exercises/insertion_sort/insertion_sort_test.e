note
	description: "Test harness for insertion sort."

class
	INSERTION_SORT_TEST

feature

	test_insertion_sort
		local
			a: SIMPLE_ARRAY [INTEGER]
			s: INSERTION_SORT
			input: MML_SEQUENCE [INTEGER]
		do
			input := << 0, -1, 2, -3, 4, -5 >>
			create a.init (input)
			create s

			s.insertion_sort (a)

			check a.sequence.count = input.count end
			check across 1 |..| a.count as i all i.item < a.count implies a[i.item] <= a[i.item+1] end end
			check a.sequence.to_bag = input.to_bag end
		end

end
