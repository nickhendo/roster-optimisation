# Notes

## Questions for Rosterer
- Can shifts only be covered by one person?
- Do breaks need to be managed, or can employees decide between them?
- Does the structure, i.e. 3 shifts per day of the same length (8.5hrs) 
  with three slots for each?
- Says 10 hours rest overnight, this is taken to mean just 10 hours break 
  between any two shifts.
- What is the qualification structure like? Are all of the supplied 
  employees qualified for all the available shifts? Should some less 
  qualified work with more qualified?
- Any employee requests for leave, particular times of day to work, etc.?
- Is this a consistent file format for both shift and employee details?

## Assumptions
 - 3 People working at a given time
 - 3 Shifts per day all at the same time

## Further improvement
- In order to emphasise consecutive days off, and similar shift starting
  times, some extra decision variables would be added. One as a count,
  representing a metric for number of consecutive days (C) off and the other
  as a measure of variance (V) for the starting times of each shift. An 
  objective function would then aim to `Maximise C/V` or something to that
  affect.
  
- A more object oriented approach, with the orm module better developed
  would also make for some more logical code. Ideally linking the rows
  that are built from the `.csv` files to their corresponding variables
  in the optimisation. It isn't clear the kind of variation that would be
  expected in these files. This would need to be investigated before
  putting too much work into developing an interface for them.
  
- Some unit tests could also be added, as well as some verification of
  the actual rosters that are generated. Something to explicitly check
  that the applied rules are being adhered to as expected.
