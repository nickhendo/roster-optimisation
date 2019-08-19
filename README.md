# Maths Developer Exercise

The aim of this exercise is to simulate real working conditions to provide context for a code/design review session. The follow up review session will focus on your reasons for model design and pseudo-code/code implementation. As such it isn’t necessary to build a complete implementation, however having some runnable code is recommended (preferably in Python).

The suggested time to spend on this exercise is at least 2 hours.

# Instructions

For this challenge, we are looking for you to create models and an engine for a use by a simple rostering application.
This application would be used for creating, editing, deleting and assigning shifts to a set of employees.
For example this application could be used for a small business that works 24/7 to manage the shifts of it's employees to make sure everyone gets adequate days off and doesn't get shifts which are directly back-to-back.

We're providing you with two mock data csv files which are typical of the type of data collected directly from clients:

Employees: The people who are being rostered
Shifts: These are the bits of work assigned to employees.

The minimum set of rules that the algorithm needs to consider are:
- Minimum of 10hr overnight rest
- Maximum of 5 days working out of 7 any rolling 7 day window
- Maximum of 5 days working in a row
- Employees can only do shifts that they are qualified for

Additional more difficult concepts which can be considered (not required):
- Fairness of spread of shifts to employees
- Strings of days off highly desirable over single days off
- Maintaining similar start time (eg 3 morning shifts in a row)

### Challenge

The amount of time you spend on this exercise is up to you, and there are several activities you could consider depending on your strengths:

- Develop some questions (for the rosterer) that support further requirements that you might need in order to more fully specify such an application.
- Create ORM definitions for the application. You could also demonstrate the effectiveness of your schemas by writing a routine to read the sample data from the provided files into your models.
- Describe and/or implement an algorithm which generates an optimised allocation of staff to shifts respecting the required rules provided above

If any of the requirements are unclear feel free to send through questions for clarification or make assumptions - we are not trying to test you on your knowledge of rostering.

What you deliver is up to you, some suggestions are:

- Python 3
- Git repository
- Pseudo-code
- Notes on assumptions or next steps you would take

When you're ready to share your solution with us, email a link to your recruiter or Biarri contact.

On completion, if there are additional things you think you could have done better/did not have enough time to complete, feel free to compile a quick list and bring it to the technical interview to help remind yourself during the discussion.
