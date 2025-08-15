ALTER TABLE recipe
ADD COLUMN d_cook_time TIME
AFTER cook_time

SELECT MAKETIME(
    IF(LOCATE('H', cook_time) > 0,
       CAST(SUBSTRING(cook_time, 3, LOCATE('H', cook_time) - 3) AS UNSIGNED),
       0),
    IF(LOCATE('M', cook_time) > 0,
       CAST(SUBSTRING(cook_time,
                      IF(LOCATE('H', cook_time) > 0, LOCATE('H', cook_time) + 1, 3),
                      LOCATE('M', cook_time) - IF(LOCATE('H', cook_time) > 0, LOCATE('H', cook_time) + 1, 3)
                     ) AS UNSIGNED),
       0),
    IF(LOCATE('S', cook_time) > 0,
       CAST(SUBSTRING(cook_time,
                      IF(LOCATE('M', cook_time) > 0, LOCATE('M', cook_time) + 1,
                         IF(LOCATE('H', cook_time) > 0, LOCATE('H', cook_time) + 1, 3)
                      ),
                      LOCATE('S', cook_time) - IF(LOCATE('M', cook_time) > 0, LOCATE('M', cook_time) + 1,
                         IF(LOCATE('H', cook_time) > 0, LOCATE('H', cook_time) + 1, 3)
                      )
                     ) AS UNSIGNED),
       0)
) AS parsed_time, cook_time
FROM recipe where cook_time is not null limit 50;


UPDATE recipe
SET d_cook_time = MAKETIME(
    IF(LOCATE('H', cook_time) > 0,
       CAST(SUBSTRING(cook_time, 3, LOCATE('H', cook_time) - 3) AS UNSIGNED),
       0),
    IF(LOCATE('M', cook_time) > 0,
       CAST(SUBSTRING(cook_time,
                      IF(LOCATE('H', cook_time) > 0, LOCATE('H', cook_time) + 1, 3),
                      LOCATE('M', cook_time) - IF(LOCATE('H', cook_time) > 0, LOCATE('H', cook_time) + 1, 3)
                     ) AS UNSIGNED),
       0),
    IF(LOCATE('S', cook_time) > 0,
       CAST(SUBSTRING(cook_time,
                      IF(LOCATE('M', cook_time) > 0, LOCATE('M', cook_time) + 1,
                         IF(LOCATE('H', cook_time) > 0, LOCATE('H', cook_time) + 1, 3)
                      ),
                      LOCATE('S', cook_time) - IF(LOCATE('M', cook_time) > 0, LOCATE('M', cook_time) + 1,
                         IF(LOCATE('H', cook_time) > 0, LOCATE('H', cook_time) + 1, 3)
                      )
                     ) AS UNSIGNED),
       0))
where cook_time is not null and id > (select max(id) from recipe where d_cook_time is not null) ORDER by id asc limit 5000;

ALTER TABLE recipe
ADD COLUMN d_prep_time TIME
AFTER prep_time

UPDATE recipe
SET d_prep_time = MAKETIME(
    IF(LOCATE('H', prep_time) > 0,
       CAST(SUBSTRING(prep_time, 3, LOCATE('H', prep_time) - 3) AS UNSIGNED),
       0),
    IF(LOCATE('M', prep_time) > 0,
       CAST(SUBSTRING(prep_time,
                      IF(LOCATE('H', prep_time) > 0, LOCATE('H', prep_time) + 1, 3),
                      LOCATE('M', prep_time) - IF(LOCATE('H', prep_time) > 0, LOCATE('H', prep_time) + 1, 3)
                     ) AS UNSIGNED),
       0),
    IF(LOCATE('S', prep_time) > 0,
       CAST(SUBSTRING(prep_time,
                      IF(LOCATE('M', prep_time) > 0, LOCATE('M', prep_time) + 1,
                         IF(LOCATE('H', prep_time) > 0, LOCATE('H', prep_time) + 1, 3)
                      ),
                      LOCATE('S', prep_time) - IF(LOCATE('M', prep_time) > 0, LOCATE('M', prep_time) + 1,
                         IF(LOCATE('H', prep_time) > 0, LOCATE('H', prep_time) + 1, 3)
                      )
                     ) AS UNSIGNED),
       0))
where prep_time is not null and id > (select max(id) from recipe where d_prep_time is not null) ORDER by id asc limit 5000;

update recipe set prep_time='PT30M' where id = 48027 limit 1
update recipe set prep_time='PT1M' where id = 235258 limit 1

ALTER TABLE recipe
ADD COLUMN d_total_time TIME
AFTER total_time

UPDATE recipe
SET d_total_time = MAKETIME(
    IF(LOCATE('H', total_time) > 0,
       CAST(SUBSTRING(total_time, 3, LOCATE('H', total_time) - 3) AS UNSIGNED),
       0),
    IF(LOCATE('M', total_time) > 0,
       CAST(SUBSTRING(total_time,
                      IF(LOCATE('H', total_time) > 0, LOCATE('H', total_time) + 1, 3),
                      LOCATE('M', total_time) - IF(LOCATE('H', total_time) > 0, LOCATE('H', total_time) + 1, 3)
                     ) AS UNSIGNED),
       0),
    IF(LOCATE('S', total_time) > 0,
       CAST(SUBSTRING(total_time,
                      IF(LOCATE('M', total_time) > 0, LOCATE('M', total_time) + 1,
                         IF(LOCATE('H', total_time) > 0, LOCATE('H', total_time) + 1, 3)
                      ),
                      LOCATE('S', total_time) - IF(LOCATE('M', total_time) > 0, LOCATE('M', total_time) + 1,
                         IF(LOCATE('H', total_time) > 0, LOCATE('H', total_time) + 1, 3)
                      )
                     ) AS UNSIGNED),
       0))
where total_time is not null and id > (select max(id) from recipe where d_total_time is not null) ORDER by id asc limit 5000;


UPDATE recipe set keywords = SUBSTR(keywords, 3, LENGTH(keywords) - 3)
where keywords like '%c(%)' limit 10000;


UPDATE recipe set recipe_ingredients = SUBSTR(recipe_ingredients, 3, LENGTH(recipe_ingredients) - 3)
where recipe_ingredients like '%c(%)' AND id = 38 limit 10000;


UPDATE recipe set recipe_instructions = SUBSTR(recipe_instructions, 3, LENGTH(recipe_instructions) - 3)
where recipe_instructions like '%c(%)' AND id = 38 limit 10000;

-- 113967

-- 151469
-- 154258
-- 229146
-- 355793
-- 462701
-- 494023
-- 514174


'"Preheat oven to 450°F In the work bowl of a food processor, combine flour, sugar, salt, baking powder, cinnamon, ginger, cloves and cardamom. Pulse processor until combined.", "Add butter and process in 1-second pulses until it resembles coarse meal, about 8-10 pulses.", "In a large bowl, whisk together milk and eggs. Add flour-butter mixture and stir until combined. It should be fairly moist; if it''s dry, crumbly, or there is still flour in the bowl, add cold water by 1/2 tablespoon increments until it all comes together.", 
"Flour a surface lightly and turn out dough. Shape into a 1\"-thick disc for regular sized scones; divide in half and make each half into a 1\"-thick disc for mini scones. Cut disc(s) into 8 wedges.", "Line a baking sheet with parchment or silicon liner. Arrange scones on sheet and bake in preheated oven 15-17 minutes until light golden-brown."'



UPDATE recipe set recipe_instructions='"Prepare Filling:", "Place potatoes in a saucepan, cover with water and chicken broth.", "Bring to a boil, reduce heat, and simmer 15 minutes or until tender.", "Drain well.", "Combine potatoes, broth, softened cream cheese, salt, pepper and salmon in a large bowl, mash until well combined.", "Heat a large nonstick skillet over medium-high heat.", "Coat pan with cooking spray and butter.", "Add onion, cook 5-10 minutes until caramelized.", "Remove with slotted spoon and add to potato mixture.", 
"Stir into the potato mixture.", "Set aside.", "Prepare Dough:", "Preheat oven to 375°F.", "Combine 2-1/2 cups flour, baking powder and salt in a large bowl.", "Combine cream cheese, 1/4 cup water, butter and 1 egg in medium bowl, stirring with a whisk.", "Make a well in center of flour mixture; add yogurt mixture, stirring until dough forms.", "Sprinkle with chopped chives, if desired.", "Turn dough out onto a floured surface.", "Knead until smooth and elastic(about 10 minutes); and 1 tablespoon flour to prevent dough from sticking to hands(dough will feel sticky).", 
"Cover dough, and let it stand for 10 minutes.", "Divide dough into 16 portions.", "Working with one portion at a time(cover remaining dough to prevent drying), roll each portion into a 5\" square on a floured board.", "Place 1/4 cup potato mixture in the center of dough.", "Fold dough over filling, pinching ends and seam to seal.", "Place knishes, seam side down on a cookie-sheet coated with cooking spray.", "Repeat procedure with remaining dough and filling.", "Make a small cut in center of top of each knish.", 
"Combine remaining 1 tablespoon water and remaining egg in a small bowl, stirring with a whisk.", "Brush egg mixture over knish tops.", "Bake for 30 minutes or until golden."' WHERE id=151469;


"Prepare Filling:", "Place potatoes in a saucepan, cover with water and chicken broth.", "Bring to a boil, reduce heat, and simmer 15 minutes or until tender.", "Drain well.", "Combine potatoes, broth, softened cream cheese, salt, pepper and salmon in a large bowl, mash until well combined.", "Heat a large nonstick skillet over medium-high heat.", "Coat pan with cooking spray and butter.", "Add onion, cook 5-10 minutes until caramelized.", "Remove with slotted spoon and add to potato mixture.", 
"Stir into the potato mixture.", "Set aside.", "Prepare Dough:", "Preheat oven to 375°F.", "Combine 2-1/2 cups flour, baking powder and salt in a large bowl.", "Combine cream cheese, 1/4 cup water, butter and 1 egg in medium bowl, stirring with a whisk.", "Make a well in center of flour mixture; add yogurt mixture, stirring until dough forms.", "Sprinkle with chopped chives, if desired.", "Turn dough out onto a floured surface.", "Knead until smooth and elastic(about 10 minutes); and 1 tablespoon flour to prevent dough from sticking to hands(dough will feel sticky).", 
"Cover dough, and let it stand for 10 minutes.", "Divide dough into 16 portions.", "Working with one portion at a time(cover remaining dough to prevent drying), roll each portion into a 5\" square on a floured board.", "Place 1/4 cup potato mixture in the center of dough.", "Fold dough over filling, pinching ends and seam to seal.", "Place knishes, seam side down on a cookie-sheet coated with cooking spray.", "Repeat procedure with remaining dough and filling.", "Make a small cut in center of top of each knish.", 
"Combine remaining 1 tablespoon water and remaining egg in a small bowl, stirring with a whisk.", "Brush egg mixture over knish tops.", "Bake for 30 minutes or until golden."



UPDATE recipe SET keywords=REPLACE(keywords, '"', '') where id=38;


UPDATE recipe SET recipe_ingredients=REPLACE(recipe_ingredients, '"', '') where id=38 limit 10000;


UPDATE recipe SET keywords=REPLACE(keywords, '"', '') WHERE keywords LIKE '%"%' limit 10000;


UPDATE recipe SET recipe_instructions=REPLACE(recipe_instructions, '"', '') WHERE recipe_instructions LIKE '%"%' limit 10000;