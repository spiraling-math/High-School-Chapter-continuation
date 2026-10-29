// backend/siteMap.js
// -----------------------------------------------------------------------------
// The ONLY pages the Spi-Math chat assistant is allowed to link to.
//
// The assistant never writes URLs itself: it answers with page KEYS, and the
// backend looks each key up here. If a page is not in this list, the bot
// cannot link to it.
//
// HOW TO EDIT (see README "Updating the site map"):
//   - key:    short, stable id (lowercase, digits, dashes). Do not rename a key
//             casually: it is what the AI picks. Keys must be unique.
//   - title:  the label shown on the link button in the chat.
//   - url:    the full https://www.spi-math.com/... address of the page.
//   - description: one plain sentence the AI reads to decide when to link it.
//   - category / audience: help the AI choose; free text.
//   - requiresEnrolment: true if visitors must have bought the course / be
//             logged in to use the page.
//   - enrollingSoon (optional): true while the course is NOT open for
//             enrolment yet ("Enrolling soon" on its program page). The AI
//             then says it cannot be bought yet. When the course opens, delete
//             `enrollingSoon: true` and the "Enrolling soon..." words at the
//             start of its description, and update the matching SITE_FACTS line.
// After any edit, Publish the site. Every edit changes the AI's instructions,
// so the first few questions afterwards cost slightly more (cache rebuild).
// A mistake in this file (for example a missing quote or comma) stops the
// whole assistant: check Wix Logs after publishing (README > Troubleshooting).
// -----------------------------------------------------------------------------

/** Short facts the assistant may state. Keep them true; prices may change. */
export const SITE_FACTS = [
  'Spi-Math (Spiraling Math OÜ, Estonia) sells self-paced, interactive maths courses online, from kindergarten (ages 3-6) through Grades 1-12, IGCSE, Cambridge A Level 9709 and Further Maths 9231, IB Diploma (AA/AI, SL/HL), AP Calculus and AP Statistics, to university courses.',
  'Each course is bought once (no subscription, nothing renews); access opens immediately after payment at the secure checkout.',
  'A single course is EUR 25 for two years of access; bundles and All-Access Premium (every course, EUR 1000, five years) are also offered. Prices can change, so always link the Enrolling and Payment page for current prices.',
  'Visitors can read a full chapter free and use the Free Content page without enrolling.',
  'Enrolled students open their courses from the Your Classroom hub.',
  'Dabdoob Town is a separate 3D town for Kindergarten to Grade 5 with 77 games and activities.',
  'Cambridge 9709 Paper 2 (P2) is an AS-only route; the full A Level needs Paper 3 (P3).',
  'Grades 2 to 12 and the university Probability and Statistics 1 and 2 courses are marked "Enrolling soon": they are not open for enrolment yet.',
  'Edexcel courses are not on sale, and live tutoring sessions cannot be booked online.',
  'Contact email: info@spi-math.com.',
];

export const SITE_MAP = [
  { key: 'home', title: 'Spi-Math home page', url: 'https://www.spi-math.com', description: 'The Spi-Math home page, the starting point for the whole site.', category: 'home', audience: 'everyone', requiresEnrolment: false },
  { key: 'courses', title: 'Interactive Maths Courses, Preschool to University', url: 'https://www.spi-math.com/copy-of-visitors-page', description: 'The main courses page: complete interactive maths chapters for IGCSE, A Level, AP and university, where you can read a full chapter free.', category: 'home', audience: 'prospective students and parents', requiresEnrolment: false },
  { key: 'programs', title: 'Programs', url: 'https://www.spi-math.com/programs', description: "The Programs page, an overview of Spi-Math's maths programs.", category: 'enrolment', audience: 'prospective students and parents', requiresEnrolment: false },
  { key: 'program-list', title: 'Program List (all online programs)', url: 'https://www.spi-math.com/challenges', description: 'The list of all Spi-Math online programs; each one opens its own program page.', category: 'enrolment', audience: 'prospective students and parents', requiresEnrolment: false },
  { key: 'enrol', title: 'Enrol', url: 'https://www.spi-math.com/enrol', description: 'The Enrol page for joining a Spi-Math course.', category: 'enrolment', audience: 'prospective students and parents', requiresEnrolment: false },
  { key: 'enrolling-and-payment', title: 'Enrolling and Payment', url: 'https://www.spi-math.com/payment-methods', description: 'How to enrol and pay: buy one course or All Access at the secure checkout, and your access opens immediately.', category: 'enrolment', audience: 'prospective students and parents', requiresEnrolment: false },
  { key: 'free-content', title: 'Free Content', url: 'https://www.spi-math.com/free-content', description: 'Free Spi-Math content you can use without enrolling.', category: 'free', audience: 'everyone', requiresEnrolment: false },
  { key: 'student-hub', title: 'Your Classroom (enrolled students hub)', url: 'https://www.spi-math.com/copy-of-participant-page', description: 'For enrolled students: open your classroom, see how every chapter is laid out, install your course as an app, and find help.', category: 'student-hub', audience: 'enrolled students', requiresEnrolment: false },
  { key: 'about-the-founder', title: 'About The Founder', url: 'https://www.spi-math.com/about-me', description: 'About the founder of Spi-Math.', category: 'about', audience: 'everyone', requiresEnrolment: false },
  { key: 'groups', title: 'Groups', url: 'https://www.spi-math.com/groups', description: 'The Spi-Math community groups page, with a public group for the site.', category: 'community', audience: 'members', requiresEnrolment: false },
  { key: 'kg-sprouts-classroom', title: 'KG Sprouts (kindergarten) classroom', url: 'https://www.spi-math.com/sprouts-classroom', description: 'Spi-Math Sprouts, a complete kindergarten maths journey for children aged 3 to 6.', category: 'courses-early-years', audience: 'parents of children aged 3 to 6', requiresEnrolment: true },
  { key: 'dabdoob-town', title: 'Dabdoob Town', url: 'https://www.spi-math.com/dabdoob-town', description: 'Dabdoob Town, a 3D town children drive through with 77 games and activities, with the whole Kindergarten to Grade 5 curriculum included.', category: 'courses-early-years', audience: 'parents of children in Kindergarten to Grade 5', requiresEnrolment: true },
  { key: 'grade-1-classroom', title: 'Grade 1 Maths classroom', url: 'https://www.spi-math.com/grade-1-classroom', description: 'A complete first-year course in 22 interactive chapters, covering counting and place value, addition and subtraction within twenty, and measurement.', category: 'courses-school', audience: 'Grade 1 students and parents', requiresEnrolment: true },
  { key: 'grade-2-classroom', title: 'Grade 2 Maths classroom', url: 'https://www.spi-math.com/grade-2-classroom', description: 'Enrolling soon, not open for enrolment yet. Grade 2 maths: two-digit addition, early multiplication ideas, time and money, taught through interactive lessons.', category: 'courses-school', audience: 'Grade 2 students and parents', requiresEnrolment: true, enrollingSoon: true },
  { key: 'grade-3-classroom', title: 'Grade 3 Maths classroom', url: 'https://www.spi-math.com/grade-3-classroom', description: 'Enrolling soon, not open for enrolment yet. Grade 3 maths covering multiplication, division, fractions and measurement, with instant feedback.', category: 'courses-school', audience: 'Grade 3 students and parents', requiresEnrolment: true, enrollingSoon: true },
  { key: 'grade-4-classroom', title: 'Grade 4 Maths classroom', url: 'https://www.spi-math.com/grade-4-classroom', description: 'Enrolling soon, not open for enrolment yet. Grade 4 maths: long multiplication, fractions, decimals and geometry, built on clear explanations.', category: 'courses-school', audience: 'Grade 4 students and parents', requiresEnrolment: true, enrollingSoon: true },
  { key: 'grade-5-classroom', title: 'Grade 5 Maths classroom', url: 'https://www.spi-math.com/grade-5-classroom', description: 'Enrolling soon, not open for enrolment yet. Grade 5 maths on fractions, decimals, percentages and volume, preparing students for middle school.', category: 'courses-school', audience: 'Grade 5 students and parents', requiresEnrolment: true, enrollingSoon: true },
  { key: 'grade-6-classroom', title: 'Grade 6 Maths classroom', url: 'https://www.spi-math.com/grade-6-classroom', description: 'Enrolling soon, not open for enrolment yet. Grade 6 maths: ratios, negative numbers, expressions and data, the first step of middle school.', category: 'courses-school', audience: 'Grade 6 students and parents', requiresEnrolment: true, enrollingSoon: true },
  { key: 'grade-7-classroom', title: 'Grade 7 Maths classroom', url: 'https://www.spi-math.com/grade-7-classroom', description: 'Enrolling soon, not open for enrolment yet. Grade 7 maths: proportional reasoning, integers, equations and geometry.', category: 'courses-school', audience: 'Grade 7 students and parents', requiresEnrolment: true, enrollingSoon: true },
  { key: 'grade-8-classroom', title: 'Grade 8 Maths classroom', url: 'https://www.spi-math.com/grade-8-classroom', description: 'Enrolling soon, not open for enrolment yet. Grade 8 maths on linear equations, functions, transformations and the Pythagorean theorem, building the bridge into high school.', category: 'courses-school', audience: 'Grade 8 students and parents', requiresEnrolment: true, enrollingSoon: true },
  { key: 'grade-9-classroom', title: 'Grade 9 Maths classroom', url: 'https://www.spi-math.com/grade-9-classroom', description: 'Enrolling soon, not open for enrolment yet. Grade 9 maths led by algebra: linear and quadratic thinking, systems and functions.', category: 'courses-school', audience: 'Grade 9 students and parents', requiresEnrolment: true, enrollingSoon: true },
  { key: 'grade-10-classroom', title: 'Grade 10 Maths classroom', url: 'https://www.spi-math.com/grade-10-classroom', description: 'Enrolling soon, not open for enrolment yet. Grade 10 maths deepening algebra, geometry and trigonometry.', category: 'courses-school', audience: 'Grade 10 students and parents', requiresEnrolment: true, enrollingSoon: true },
  { key: 'grade-11-classroom', title: 'Grade 11 Maths classroom', url: 'https://www.spi-math.com/grade-11-classroom', description: 'Enrolling soon, not open for enrolment yet. Grade 11 maths spanning advanced algebra, trigonometry and precalculus foundations.', category: 'courses-school', audience: 'Grade 11 students and parents', requiresEnrolment: true, enrollingSoon: true },
  { key: 'grade-12-classroom', title: 'Grade 12 Maths classroom', url: 'https://www.spi-math.com/grade-12-classroom', description: 'Enrolling soon, not open for enrolment yet. The final year of school maths: limits, calculus foundations, probability and exam-style practice.', category: 'courses-school', audience: 'Grade 12 students and parents', requiresEnrolment: true, enrollingSoon: true },
  { key: 'igcse-classroom', title: 'IGCSE Mathematics classroom', url: 'https://www.spi-math.com/igcse-classroom', description: 'IGCSE Mathematics in 38 interactive chapters covering number, algebra, geometry, trigonometry and statistics, with exam-style practice.', category: 'courses-igcse-alevel', audience: 'IGCSE students', requiresEnrolment: true },
  { key: 'cambridge-9709-p1-classroom', title: 'Cambridge A Level 9709 Pure Mathematics 1 (P1) classroom', url: 'https://www.spi-math.com/cambridge-p1-classroom', description: 'Cambridge 9709 Paper 1: quadratics, functions, coordinate geometry, circular measure, trigonometry, series, differentiation and integration; compulsory for AS and A Level.', category: 'courses-igcse-alevel', audience: 'Cambridge AS/A Level Mathematics students', requiresEnrolment: true },
  { key: 'cambridge-9709-p2-classroom', title: 'Cambridge A Level 9709 Pure Mathematics 2 (P2) classroom', url: 'https://www.spi-math.com/cambridge-p2-classroom', description: 'Cambridge 9709 Paper 2: algebra, logarithms and exponentials, trigonometry, calculus and numerical solution of equations; an AS-only route.', category: 'courses-igcse-alevel', audience: 'Cambridge AS Level Mathematics students', requiresEnrolment: true },
  { key: 'cambridge-9709-p3-classroom', title: 'Cambridge A Level 9709 Pure Mathematics 3 (P3) classroom', url: 'https://www.spi-math.com/cambridge-p3-classroom', description: 'Cambridge 9709 Paper 3: everything in Paper 2 plus vectors, differential equations and complex numbers; compulsory for the full A Level.', category: 'courses-igcse-alevel', audience: 'Cambridge A Level Mathematics students', requiresEnrolment: true },
  { key: 'cambridge-9709-m1-classroom', title: 'Cambridge A Level 9709 Mechanics (M1) classroom', url: 'https://www.spi-math.com/cambridge-9709-m1-classroom', description: "Cambridge 9709 Paper 4, Mechanics: forces and equilibrium, straight-line kinematics, momentum, Newton's laws, energy, work and power.", category: 'courses-igcse-alevel', audience: 'Cambridge AS/A Level Mathematics students', requiresEnrolment: true },
  { key: 'cambridge-9709-s1-classroom', title: 'Cambridge A Level 9709 Probability and Statistics 1 (S1) classroom', url: 'https://www.spi-math.com/cambridge-s1-classroom', description: 'Cambridge 9709 Paper 5: representation of data, permutations and combinations, probability, discrete random variables and the Normal distribution.', category: 'courses-igcse-alevel', audience: 'Cambridge AS/A Level Mathematics students', requiresEnrolment: true },
  { key: 'cambridge-9709-s2-classroom', title: 'Cambridge A Level 9709 Probability and Statistics 2 (S2) classroom', url: 'https://www.spi-math.com/cambridge-s2-classroom', description: 'Cambridge 9709 Paper 6: the Poisson distribution, linear combinations of random variables, continuous random variables, sampling and estimation, and hypothesis tests.', category: 'courses-igcse-alevel', audience: 'Cambridge A Level Mathematics students', requiresEnrolment: true },
  { key: 'cambridge-9231-fp1-classroom', title: 'Cambridge A Level 9231 Further Pure Mathematics 1 (FP1) classroom', url: 'https://www.spi-math.com/cambridge-fp1-classroom-9231', description: 'Cambridge Further Maths 9231 Paper 1: roots of polynomial equations, rational functions, summation of series, matrices, polar coordinates, vectors and proof by induction.', category: 'courses-igcse-alevel', audience: 'Cambridge A Level Further Mathematics students', requiresEnrolment: true },
  { key: 'cambridge-9231-fp2-classroom', title: 'Cambridge A Level 9231 Further Pure Mathematics 2 (FP2) classroom', url: 'https://www.spi-math.com/cambridge-9231-fp2-classroom', description: "Cambridge Further Maths 9231 Paper 2: hyperbolic functions, matrices and eigenvalues, calculus, complex numbers with de Moivre's theorem, and differential equations.", category: 'courses-igcse-alevel', audience: 'Cambridge A Level Further Mathematics students', requiresEnrolment: true },
  // URL slug is misspelled ("cambrdige") and says 9709 on the live site; the content is
  // Cambridge 9231 Further Mathematics Paper 3. Keep the URL exactly as published.
  { key: 'cambridge-fm-classroom', title: 'Cambridge Further Mechanics (FM) classroom', url: 'https://www.spi-math.com/cambrdige-9709-fm-classroom', description: "Cambridge Further Mechanics: projectile motion, equilibrium of a rigid body, circular motion, Hooke's law, variable-force motion, momentum and restitution.", category: 'courses-igcse-alevel', audience: 'Cambridge A Level Further Mathematics students', requiresEnrolment: true },
  { key: 'cambridge-9231-fps-classroom', title: 'Cambridge A Level 9231 Further Probability and Statistics (FPS) classroom', url: 'https://www.spi-math.com/cambridge-further-statistics-9231', description: 'Cambridge Further Maths 9231 Paper 4: continuous random variables, t-distribution inference, chi-squared tests, non-parametric tests and probability generating functions.', category: 'courses-igcse-alevel', audience: 'Cambridge A Level Further Mathematics students', requiresEnrolment: true },
  { key: 'ibdp-aasl-classroom', title: 'IB Diploma Maths Analysis and Approaches SL (AA SL) classroom', url: 'https://www.spi-math.com/ibdp-aasl-classroom', description: 'IB Mathematics Analysis and Approaches Standard Level: the full two-year course in 32 interactive chapters.', category: 'courses-ib', audience: 'IB Diploma students', requiresEnrolment: true },
  { key: 'ibdp-aahl-classroom', title: 'IB Diploma Maths Analysis and Approaches HL (AA HL) classroom', url: 'https://www.spi-math.com/ibdp-aahl-classroom', description: 'IB Mathematics Analysis and Approaches Higher Level: the full two-year course in 50 interactive chapters.', category: 'courses-ib', audience: 'IB Diploma students', requiresEnrolment: true },
  { key: 'ibdp-aisl-classroom', title: 'IB Diploma Maths Applications and Interpretation SL (AI SL) classroom', url: 'https://www.spi-math.com/ibdp-aisl-classroom', description: 'IB Mathematics Applications and Interpretation Standard Level: the full two-year course in 22 interactive chapters, focused on modelling and statistics.', category: 'courses-ib', audience: 'IB Diploma students', requiresEnrolment: true },
  { key: 'ibdp-aihl-classroom', title: 'IB Diploma Maths Applications and Interpretation HL (AI HL) classroom', url: 'https://www.spi-math.com/ibdp-aihl-classroom', description: 'IB Mathematics Applications and Interpretation Higher Level: the full two-year course in 40 interactive chapters, including advanced statistics, calculus and graph theory.', category: 'courses-ib', audience: 'IB Diploma students', requiresEnrolment: true },
  { key: 'ap-calculus-classroom', title: 'AP Calculus classroom', url: 'https://www.spi-math.com/ap-calculus-classroom', description: 'AP Calculus in 10 interactive chapters, from limits and continuity through differentiation and beyond.', category: 'courses-ap', audience: 'AP students', requiresEnrolment: true },
  { key: 'ap-statistics-classroom', title: 'AP Statistics classroom', url: 'https://www.spi-math.com/ap-statistics-classroom', description: 'AP Statistics in 9 interactive chapters, covering one- and two-variable data, collecting data, probability and more.', category: 'courses-ap', audience: 'AP students', requiresEnrolment: true },
  { key: 'calculus-1-classroom', title: 'Calculus 1: Differential Calculus classroom', url: 'https://www.spi-math.com/calculus-1-classroom', description: 'A complete university differential calculus course in 18 chapters, from functions and limits through the derivative.', category: 'courses-university', audience: 'university students', requiresEnrolment: true },
  { key: 'calculus-2-classroom', title: 'Calculus 2: Integral Calculus classroom', url: 'https://www.spi-math.com/calculus-2-classroom', description: 'A complete university integral calculus course in 16 chapters, from the definite integral and integration techniques to areas and volumes.', category: 'courses-university', audience: 'university students', requiresEnrolment: true },
  { key: 'calculus-3-classroom', title: 'Calculus 3: Multivariable Calculus classroom', url: 'https://www.spi-math.com/calculus-3-classroom', description: 'A complete university multivariable calculus course in 28 chapters, from vectors through partial derivatives and multiple integrals.', category: 'courses-university', audience: 'university students', requiresEnrolment: true },
  { key: 'linear-algebra-classroom', title: 'Linear Algebra classroom', url: 'https://www.spi-math.com/linear-algebra-classroom', description: 'A complete university linear algebra course in 20 interactive chapters, from systems of equations and matrix algebra to vector spaces.', category: 'courses-university', audience: 'university students', requiresEnrolment: true },
  { key: 'number-theory-classroom', title: 'Introduction to Number Theory classroom', url: 'https://www.spi-math.com/number-theory-classroom', description: "Number theory in 14 chapters, from induction and the Euclidean algorithm through congruences, Euler's phi function and RSA to quadratic reciprocity.", category: 'courses-university', audience: 'university students', requiresEnrolment: true },
  { key: 'complex-analysis-1-classroom', title: 'Complex Analysis 1 classroom', url: 'https://www.spi-math.com/complex-analysis-1-classroom', description: "Complex Analysis I in 14 chapters, from complex numbers to conformal mapping, including Cauchy's theorem, Laurent series and residues.", category: 'courses-university', audience: 'university students', requiresEnrolment: true },
  { key: 'complex-analysis-2-classroom', title: 'Complex Analysis 2 classroom', url: 'https://www.spi-math.com/complex-analysis-2-classroom', description: 'Complex Analysis II in 14 chapters: the Riemann mapping theorem, analytic continuation, the gamma and zeta functions, elliptic functions and Riemann surfaces.', category: 'courses-university', audience: 'university students', requiresEnrolment: true },
  { key: 'probability-statistics-1-classroom', title: 'Probability and Statistics 1 classroom', url: 'https://www.spi-math.com/proba-stat-1-classroom', description: 'Enrolling soon, not open for enrolment yet. A university probability and statistics course from counting rules to hypothesis testing, taught with simulations and real data.', category: 'courses-university', audience: 'university students', requiresEnrolment: true, enrollingSoon: true },
  { key: 'probability-statistics-2-classroom', title: 'Probability and Statistics 2 (Advanced) classroom', url: 'https://www.spi-math.com/blank-2', description: 'Enrolling soon, not open for enrolment yet. Advanced probability and statistics: estimation theory, stochastic ideas and advanced inference.', category: 'courses-university', audience: 'university students', requiresEnrolment: true, enrollingSoon: true },
  { key: 'terms-and-conditions', title: 'Terms & Conditions', url: 'https://www.spi-math.com/terms-and-conditions', description: "The site's terms and conditions.", category: 'legal', audience: 'everyone', requiresEnrolment: false },
  { key: 'privacy-policy', title: 'Privacy Policy', url: 'https://www.spi-math.com/blank', description: 'How Spi-Math handles your personal data.', category: 'legal', audience: 'everyone', requiresEnrolment: false },
  { key: 'refund-policy', title: 'Refund Policy', url: 'https://www.spi-math.com/blank-3', description: "Spi-Math's refund policy.", category: 'legal', audience: 'everyone', requiresEnrolment: false },
  { key: 'accessibility-statement', title: 'Accessibility Statement', url: 'https://www.spi-math.com/blank-1', description: "Spi-Math's accessibility statement.", category: 'legal', audience: 'everyone', requiresEnrolment: false },
];

/** Pages used by the friendly fallback reply when the AI cannot answer. */
export const FALLBACK_LINK_KEYS = ['programs', 'enrol'];

/*
 * EXCLUDED on purpose (never link these):
 *   /cart-page                - utility page (noindex), never a destination
 *   /thank-you-page           - utility page (noindex), shown only after checkout
 *   /search                   - search results utility page
 *   /kg-test                  - test page
 *   /copy-of-programs         - "Visitors Page", probable older duplicate of /copy-of-visitors-page.
 *                               Re-add if it is still linked in the site menu.
 *   /book-online              - Bookings page, but there are 0 bookable services. Re-add (category
 *                               'booking') if services are created.
 *   /challenge-page/<edexcel-ial-*, grade-9-math .. grade-12-math, probability-and-statistics,
 *                    advanced-probability-and-statistics>
 *                             - 20 Online Programs with SECRET access, hidden from visitors. Never link.
 *   /challenge-page/<slug>    - PUBLIC Online Programs pages (dynamic app pages). Optional: the
 *                               classroom pages are listed instead. Public slugs:
 *       igcse-mathematics, spi-math-sprouts, grade-1-math .. grade-8-math (2-8 say "Enrolling soon"),
 *
 * ENROLLING SOON (checked in Online Programs on 2026-10-29): the program descriptions of
 *   grade-2-math .. grade-12-math, probability-and-statistics and advanced-probability-and-statistics
 *   start with "Enrolling soon." Their classroom pages are marked enrollingSoon: true above.
 *       cambridge-9709-pure-mathematics-1/-2/-3, cambridge-9709-mechanics-1,
 *       cambridge-9709-probability-and-statistics-1/-2, cambridge-9231-further-pure-mathematics-1/-2,
 *       cambridge-9231-further-mechanics, cambridge-9231-further-probability-and-statistics,
 *       ib-math-aa-sl, ib-math-aa-hl, ib-math-ai-sl, ib-math-ai-hl, ap-calculus, ap-statistics,
 *       calculus-1-differential, calculus-2-integral, calculus-3-multivariable, linear-algebra,
 *       number-theory, complex-analysis, complex-analysis-2
 *
 * UNCERTAIN (check in the editor, Page Settings > Permissions):
 *   - requiresEnrolment=true on classroom pages is inferred from matching paid plans.
 *   - dabdoob-town may be a public landing page (then set requiresEnrolment: false).
 *   - student-hub is public but aimed at enrolled students.
 */
