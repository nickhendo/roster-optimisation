# Notes

## Setup (on Ubuntu)
- Setup a python virtual environment and clone this inside
- Source the virtual environments and install dependencies
```
source <path/to/virtual/env>/bin/activate
cd biarri-optimisation-task
pip3 install -r requirements.txt
```

## Running script
- Running should be as straightforward as 
```
python3 roster_optimisation.py
```
- The generated rosters will be printed to the console.

## Questions for Rosterer
- Must any given shift only be covered by one person?
- Do breaks need to be managed, or can employees decide between them?
- Does the structure, i.e. 3 shifts per day of the same length (8.5hrs) 
  with three slots for each ever change?
- What is the qualification structure like? Are all of the supplied 
  employees qualified for all the available shifts? Should some less 
  qualified work with more qualified? Can an employees level be in the csv
  along with their name, and the level requirements for a particular shift
  be added to the corresponding shift in the shifts csv?
- Any employee requests for leave, particular times of day to work, etc.?
- Is this a consistent file format for both shift and employee details?

## Assumptions
 - 3 People working at a given time (indicated by three shifts per timeslot)
 - 3 Timeslots per day all with the same start and end times each day
 - The spec says 10 hours rest overnight, this is taken to mean just 10 hours break 
  between any two shifts, which translates to at least two shifts gap between any two
  worked shifts.

## Further improvement
- If there is to be a rolling usage of this project, it goes without saying, that
  unit testing is a must. A set of test cases ensuring that all of the requirements
  are satisfied on a generated roster to begin with. 

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
  
- Reworking the script to accept arguments, etc. or to interface with
  a web application would also be necessary to make this more practical.
  
- Some unit tests could also be added, as well as some verification of
  the actual rosters that are generated. Something to explicitly check
  that the applied rules are being adhered to as expected.

- A more dynamic approach to the number of timeslots and shifts per day
  would also be better (not to mention a better naming convention, I
  confused myself a few times with this one, but couldn't come up with
  anything better). At the moment, they are assumed to be unchanging,
  but even if this is the case, dynamically setting these for each day
  would allow for even just unexpected roster changes that may need to
  be accounted for in the future.

