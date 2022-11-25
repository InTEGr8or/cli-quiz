Feature: Missing Item
    A question which displays a list of all but one item of a set, and asks the user to choose the missing item from a second list.

    Scenario: Display list of valid items with one item omitted 
        Given there are x=>range(2,7) valid items in the set

        When I take the test

        Then I should see x-1 items