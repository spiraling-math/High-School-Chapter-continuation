from __future__ import annotations

import html
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "spi-math-ibdp-aasl"
DOCS = PROJECT / "documents"
ZIP_PATH = ROOT / "High School.zip"
SAMPLE_HTML = "High School/hs-G7-the-normal-distribution.html"


@dataclass(frozen=True)
class Question:
    mode: str
    marks: int
    prompt: str
    answer: str
    solution: str = ""
    visual: str = ""


QUESTIONS_PER_CHAPTER = 80


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def slug(n: int, title: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return f"aasl-{n:02d}-{cleaned}.html"


CHAPTERS = [
    {
        "n": 1,
        "title": "From Patterns to Generalizations: Sequences and Series",
        "subtitle": "Sequences, series, sigma notation, arithmetic/geometric models, and the binomial theorem",
        "toc": [
            "1.1 Number patterns and sigma notation",
            "1.2 Arithmetic and geometric sequences",
            "1.3 Arithmetic and geometric series",
            "1.4 Applications of arithmetic and geometric patterns",
            "1.5 The binomial theorem",
            "1.6 Proofs",
        ],
        "syllabus": [
            "Use arithmetic and geometric sequences and series to model real contexts.",
            "Use sigma notation and finite/infinite sums where appropriate.",
            "Use the binomial theorem for positive integer powers.",
            "Interpret parameters, limitations, and validity of a sequence model.",
        ],
        "source_html": [
            "hs-A9-sequences-and-series.html",
            "hs-A10-the-binomial-theorem.html",
            "hs-A11-mathematical-induction.html",
        ],
        "learn": [
            ("Pattern language", "A sequence is an ordered list; a series is the sum of terms. The central decision is whether the constant change is additive or multiplicative."),
            ("Arithmetic models", "For an arithmetic sequence, $u_n=u_1+(n-1)d$ and $S_n=\\frac n2(2u_1+(n-1)d)$."),
            ("Geometric models", "For a geometric sequence, $u_n=u_1r^{n-1}$ and $S_n=\\frac{u_1(1-r^n)}{1-r}$ for $r\\ne1$. If $|r|<1$, $S_\\infty=\\frac{u_1}{1-r}$."),
            ("Binomial theorem", "For integer $n\\ge0$, $(a+b)^n=\\sum_{k=0}^{n}\\binom nk a^{n-k}b^k$."),
        ],
        "worked": [
            ("Choosing a model", "A scholarship pays 600 BHD in year 1 and increases by 45 BHD each year. This is arithmetic because the increase is constant. Year 12 is $600+11(45)=1095$ BHD."),
            ("Infinite sum", "A ball rebounds to 72% of its previous height from 2.5 m. Total upward rebound distance is $2.5(0.72)/(1-0.72)=6.43$ m."),
        ],
        "questions": [
            Question("Paper 1", 6, "An arithmetic sequence has $u_1=7$ and $d=4$. Find $u_{20}$ and $S_{20}$.", "$u_{20}=83$, $S_{20}=900$."),
            Question("Paper 1", 5, "A geometric sequence has first term 80 and ratio 0.85. Find $u_6$ and state whether the infinite series converges.", "$u_6=80(0.85)^5\\approx35.5$; it converges because $|0.85|<1$."),
            Question("Paper 1", 6, "Show that $\\sum_{k=1}^{n}(3k-2)=\\frac{3n^2-n}{2}$, and hence find the sum for $n=25$.", "Use $3\\sum k-2n$; result $925$."),
            Question("Paper 1", 5, "Find the coefficient of $x^3$ in $(1+2x)^6$.", "$\\binom63(2x)^3=160x^3$, coefficient $160$."),
            Question("Paper 2", 7, "A car loses 18% of its value each year. It is bought for 9500 BHD. Model the value after $n$ years and find when it first falls below 4000 BHD.", "$V_n=9500(0.82)^n$; solve $9500(0.82)^n<4000$, first after 5 years."),
            Question("Paper 2", 6, "A savings plan deposits 40 BHD at the end of each month at a monthly growth factor of 1.004. Write a finite geometric sum for the value after 24 deposits.", "$40(1+1.004+\\cdots+1.004^{23})=40\\frac{1.004^{24}-1}{0.004}$."),
            Question("Paper 1", 4, "Expand $(2-x)^5$ up to and including the term in $x^2$.", "$32-80x+80x^2+\\cdots$."),
            Question("Paper 2", 8, "A pattern has $S_n=2n^2+3n$. Find $u_n$ and decide whether the sequence is arithmetic.", "$u_n=S_n-S_{n-1}=4n+1$; arithmetic with common difference 4."),
        ],
    },
    {
        "n": 2,
        "title": "Representing Relationships: Introducing Functions",
        "subtitle": "Domain, range, notation, composite functions, inverses, and graph windows",
        "toc": [
            "2.1 What is a function?",
            "2.2 Functional notation",
            "2.3 Drawing graphs of functions",
            "2.4 Domain and range",
            "2.5 Composite functions",
            "2.6 Inverse functions",
        ],
        "syllabus": [
            "Represent functions symbolically, graphically, numerically, and verbally.",
            "Find domain and range for common SL functions.",
            "Use composite and inverse functions, including restrictions for one-to-one behaviour.",
            "Use technology to choose appropriate graph windows and interpret features.",
        ],
        "source_html": [
            "hs-B1-functions-domain-range-composition-inverse.html",
            "hs-B2-transformations-and-graph-behaviour.html",
            "hs-B3-linear-functions-and-systems.html",
        ],
        "learn": [
            ("Function rule", "A function assigns exactly one output to each input in its domain."),
            ("Domain and range", "The domain is the allowable set of inputs. The range is the set of outputs actually produced."),
            ("Composition", "$(g\\circ f)(x)=g(f(x))$. The output of $f$ must be allowed as an input of $g$."),
            ("Inverse", "An inverse reverses a one-to-one mapping. Algebraically, swap $x$ and $y$ and solve for $y$."),
        ],
        "worked": [
            ("Inverse function", "For $f(x)=\\frac{3x-2}{5}$, set $y=\\frac{3x-2}{5}$, then $x=\\frac{5y+2}{3}$. So $f^{-1}(x)=\\frac{5x+2}{3}$."),
            ("Composite function", "If $f(x)=2x-3$ and $g(x)=x^2+1$, then $(g\\circ f)(4)=g(5)=26$."),
        ],
        "questions": [
            Question("Paper 1", 5, "For $f(x)=2x-3$ and $g(x)=x^2+1$, find $(g\\circ f)(x)$.", "$(g\\circ f)(x)=(2x-3)^2+1=4x^2-12x+10$."),
            Question("Paper 1", 4, "Find the inverse of $f(x)=\\frac{3x-2}{5}$.", "$f^{-1}(x)=\\frac{5x+2}{3}$."),
            Question("Paper 1", 4, "State the domain of $h(x)=\\sqrt{5-2x}$.", "$x\\le 2.5$."),
            Question("Paper 1", 5, "The function $p(x)=x^2-4$ has domain $x\\ge0$. State its range and inverse.", "Range $y\\ge-4$; $p^{-1}(x)=\\sqrt{x+4}$."),
            Question("Paper 2", 6, "A taxi fare is modelled by $C(d)=1.2d+2.5$. Interpret the gradient and intercept.", "Gradient: 1.2 BHD per km; intercept: fixed starting charge 2.5 BHD."),
            Question("Paper 1", 5, "If $(f\\circ g)(x)=3x+7$ and $g(x)=x-2$, find a possible $f(x)$.", "$f(x)=3x+13$."),
            Question("Paper 2", 7, "The graph of $y=f(x)$ is only visible for $-3\\le x\\le4$. Explain why this may not be the mathematical domain.", "A graph window is a viewing choice; the mathematical domain depends on the rule and restrictions."),
            Question("Paper 1", 6, "Solve $f^{-1}(a)=4$ for $a$ when $f(x)=5x-1$.", "$a=f(4)=19$."),
        ],
    },
    {
        "n": 3,
        "title": "Modelling Relationships: Linear and Quadratic Functions",
        "subtitle": "Gradients, transformations, quadratic graphs, equations, discriminants, and applications",
        "toc": [
            "3.1 Gradient of a linear function",
            "3.2 Linear functions",
            "3.3 Transformations of functions",
            "3.4 Graphing quadratic functions",
            "3.5 Solving quadratic equations",
            "3.6 The quadratic formula and discriminant",
            "3.7 Applications of quadratics",
        ],
        "syllabus": [
            "Use linear and quadratic functions to model real situations.",
            "Identify intercepts, gradients, vertices, and axes of symmetry.",
            "Solve quadratic equations by factorization, completing the square, and formula.",
            "Use the discriminant to interpret number of real solutions.",
        ],
        "source_html": [
            "hs-B3-linear-functions-and-systems.html",
            "hs-B4-quadratic-functions-and-equations.html",
            "hs-B2-transformations-and-graph-behaviour.html",
        ],
        "learn": [
            ("Linear rate", "The gradient is a constant rate of change: $m=\\frac{\\Delta y}{\\Delta x}$."),
            ("Quadratic shape", "A quadratic has the form $ax^2+bx+c$. Its vertex gives a maximum or minimum when $a\\ne0$."),
            ("Discriminant", "For $ax^2+bx+c=0$, $\\Delta=b^2-4ac$ decides the number of real roots."),
            ("Applications", "Quadratic models appear in area, projectile height, revenue, and optimization contexts."),
        ],
        "worked": [
            ("Vertex form", "$x^2-6x+11=(x-3)^2+2$, so the minimum point is $(3,2)$."),
            ("Discriminant", "$2x^2+kx+8=0$ has one solution when $k^2-64=0$, so $k=\\pm8$."),
        ],
        "questions": [
            Question("Paper 1", 4, "Find the equation of the line through $(2,5)$ and $(6,17)$.", "Gradient $3$; equation $y=3x-1$."),
            Question("Paper 1", 5, "Write $x^2-8x+10$ in completed-square form.", "$(x-4)^2-6$."),
            Question("Paper 1", 5, "Solve $2x^2-5x-3=0$.", "$x=3$ or $x=-\\frac12$."),
            Question("Paper 1", 5, "Find the values of $k$ for which $x^2+kx+9=0$ has two equal roots.", "$k=\\pm6$."),
            Question("Paper 2", 7, "A ball has height $h(t)=-5t^2+20t+1$. Find the maximum height and when it occurs.", "Vertex at $t=2$; maximum height $21$ m."),
            Question("Paper 2", 6, "A rectangle has perimeter 40 cm. Express its area in terms of one side $x$ and find the maximum area.", "$A=x(20-x)$; maximum $100$ cm^2."),
            Question("Paper 1", 5, "The graph of $y=f(x)$ is shifted 3 units right and 2 units down. Write the transformed function.", "$y=f(x-3)-2$."),
            Question("Paper 2", 8, "Revenue is $R(x)=-2x^2+48x$ for $x$ items in hundreds. Find the break-even output if fixed cost is 160.", "Solve $-2x^2+48x=160$: $x=4$ or $20$ hundreds."),
        ],
    },
    {
        "n": 4,
        "title": "Equivalent Representations: Rational Functions",
        "subtitle": "Reciprocal functions, rational transformations, asymptotes, and equivalent forms",
        "toc": [
            "4.1 The reciprocal function",
            "4.2 Transforming the reciprocal function",
            "4.3 Rational functions of the form $f(x)=\\frac{ax+b}{cx+d}$",
        ],
        "syllabus": [
            "Recognize reciprocal and rational function forms.",
            "Identify vertical and horizontal asymptotes from algebraic structure.",
            "Move between algebraic and graphical representations.",
            "Use rational functions in context while respecting domain restrictions.",
        ],
        "source_html": [
            "hs-B5-polynomial-and-rational-functions.html",
            "hs-A6-polynomials-and-algebraic-fractions.html",
            "hs-B2-transformations-and-graph-behaviour.html",
        ],
        "learn": [
            ("Reciprocal base", "The graph $y=\\frac1x$ has asymptotes $x=0$ and $y=0$."),
            ("Transformations", "$y=\\frac{a}{x-h}+k$ has vertical asymptote $x=h$ and horizontal asymptote $y=k$."),
            ("Restrictions", "The denominator cannot be zero, so rational functions often have excluded domain values."),
            ("Equivalent forms", "Algebraic rearrangement can reveal asymptotes, intercepts, or transformations."),
        ],
        "worked": [
            ("Asymptotes", "$f(x)=\\frac{3}{x-2}+5$ has asymptotes $x=2$ and $y=5$."),
            ("Solving", "$\\frac{2x+1}{x-3}=4$ gives $2x+1=4x-12$, so $x=\\frac{13}{2}$, with $x\\ne3$."),
        ],
        "questions": [
            Question("Paper 1", 4, "State the asymptotes of $f(x)=\\frac{4}{x+1}-3$.", "$x=-1$ and $y=-3$."),
            Question("Paper 1", 5, "Find the domain of $g(x)=\\frac{2x-5}{x^2-9}$.", "$x\\ne -3,3$."),
            Question("Paper 1", 5, "Solve $\\frac{x+2}{x-1}=3$.", "$x=\\frac52$."),
            Question("Paper 2", 6, "A speed model is $t(v)=\\frac{120}{v}$ hours. Explain the meaning of the asymptote.", "As $v$ increases, time approaches 0 but cannot be negative; $v=0$ is not allowed."),
            Question("Paper 1", 6, "Write $\\frac{2x+5}{x+1}$ in the form $a+\\frac{b}{x+1}$.", "$2+\\frac{3}{x+1}$."),
            Question("Paper 1", 4, "Find the $x$-intercept of $f(x)=\\frac{3x-6}{x+4}$.", "$x=2$."),
            Question("Paper 2", 7, "The average cost is $C(x)=12+\\frac{300}{x}$ for $x$ items. Find $x$ when average cost is 20.", "$12+300/x=20$, so $x=37.5$ items; context may require 38."),
            Question("Paper 1", 5, "Describe the transformation from $y=\\frac1x$ to $y=\\frac{-2}{x-4}+1$.", "Reflect/stretch by factor 2, shift 4 right and 1 up."),
        ],
    },
    {
        "n": 5,
        "title": "Measuring Change: Differentiation",
        "subtitle": "Limits, derivative functions, differentiation rules, graph interpretation, optimization, and kinematics",
        "toc": [
            "5.1 Limits and convergence",
            "5.2 The derivative function",
            "5.3 Differentiation rules",
            "5.4 Graphical interpretation of first and second derivatives",
            "5.5 Applications of differential calculus",
        ],
        "syllabus": [
            "Interpret the derivative as gradient and instantaneous rate of change.",
            "Differentiate polynomial and related functions required at SL.",
            "Use first and second derivative information to analyze graphs.",
            "Solve optimization and kinematics problems with appropriate units.",
        ],
        "source_html": [
            "hs-E1-limits-and-continuity.html",
            "hs-E2-introduction-to-differentiation.html",
            "hs-E3-differentiation-techniques.html",
            "hs-E5-curve-sketching-and-optimisation.html",
            "hs-I1-kinematics-motion-graphs-constant-acceleration.html",
        ],
        "learn": [
            ("Derivative", "$f'(x)$ gives the gradient of the tangent and the instantaneous rate of change."),
            ("Power rule", "If $f(x)=ax^n$, then $f'(x)=anx^{n-1}$ for the powers used at SL."),
            ("Stationary points", "Solve $f'(x)=0$ and classify using sign changes or $f''(x)$."),
            ("Optimization", "Define variables, build a function, differentiate, solve, and check the context."),
        ],
        "worked": [
            ("Tangent", "For $f(x)=x^3-4x$, $f'(x)=3x^2-4$. At $x=2$, gradient is 8 and point is $(2,0)$, so tangent is $y=8x-16$."),
            ("Minimum", "For $f(x)=x^2-6x+8$, $f'(x)=2x-6=0$ gives $x=3$, and $f''(x)=2>0$, so this is a minimum."),
        ],
        "questions": [
            Question("Paper 1", 5, "Differentiate $f(x)=4x^3-5x^2+7$.", "$f'(x)=12x^2-10x$."),
            Question("Paper 1", 6, "Find the equation of the tangent to $y=x^2+3x$ at $x=2$.", "Point $(2,10)$, gradient 7, tangent $y=7x-4$."),
            Question("Paper 1", 6, "Find and classify the stationary point of $f(x)=x^2-10x+3$.", "$x=5$, $f(5)=-22$, minimum."),
            Question("Paper 2", 8, "A rectangle has area 48 and perimeter $P=2x+\\frac{96}{x}$. Find the minimum perimeter.", "$P'=2-96/x^2=0$, $x=4\\sqrt6$, minimum $16\\sqrt6\\approx39.2$."),
            Question("Paper 1", 5, "If $s(t)=t^3-6t^2+9t$, find the velocity at $t=4$.", "$v(t)=3t^2-12t+9$, so $v(4)=9$."),
            Question("Paper 2", 7, "The derivative of a profit function is $P'(x)=-6x+54$. Find the output that maximizes profit and explain.", "$x=9$; derivative changes from positive to negative."),
            Question("Paper 1", 5, "Find $f''(x)$ for $f(x)=2x^4-x^3+5x$.", "$f''(x)=24x^2-6x$."),
            Question("Paper 2", 8, "A curve has $f'(x)=3x^2-12x+9$. Determine where $f$ is increasing.", "$3(x-1)(x-3)>0$, so increasing for $x<1$ or $x>3$."),
        ],
    },
    {
        "n": 6,
        "title": "Representing Data: Statistics for Univariate Data",
        "subtitle": "Sampling, data displays, central tendency, dispersion, and interpretation",
        "toc": [
            "6.1 Sampling",
            "6.2 Presentation of data",
            "6.3 Measures of central tendency",
            "6.4 Measures of dispersion",
        ],
        "syllabus": [
            "Use appropriate sampling methods and recognize bias.",
            "Represent univariate data with tables, charts, histograms, box plots, and cumulative frequency.",
            "Calculate and interpret mean, median, quartiles, IQR, variance, and standard deviation.",
            "Compare distributions using center, spread, and outliers.",
        ],
        "source_html": [
            "hs-G19-descriptive-statistics.html",
            "hs-G16-study-and-experimental-design.html",
            "hs-G15-bivariate-data-time-series-and-forecasting.html",
        ],
        "learn": [
            ("Sampling", "A good sample is representative. Bias in method or wording weakens conclusions."),
            ("Center", "Mean uses all values; median resists extreme values."),
            ("Spread", "IQR measures middle spread; standard deviation measures typical distance from the mean."),
            ("Comparison", "Compare shape, center, spread, and unusual values, always in context."),
        ],
        "worked": [
            ("Mean and median", "For 3, 5, 6, 6, 20, the mean is 8 and the median is 6. The outlier pulls the mean upward."),
            ("IQR", "If $Q_1=18$ and $Q_3=31$, then IQR is 13 and the lower outlier fence is $18-1.5(13)=-1.5$."),
        ],
        "questions": [
            Question("Paper 1", 4, "Find the mean of 4, 7, 8, 11, 20.", "$10$."),
            Question("Paper 1", 5, "For data with $Q_1=12$ and $Q_3=28$, find the IQR and upper outlier fence.", "IQR $16$; fence $28+1.5(16)=52$."),
            Question("Paper 2", 6, "A sample is taken by asking only students in the library. Name the sampling issue and explain.", "Convenience sampling; may over-represent library users and bias results."),
            Question("Paper 1", 5, "A frequency table has values 1,2,3 with frequencies 4,5,1. Find the mean.", "$(4+10+3)/10=1.7$."),
            Question("Paper 2", 6, "Two classes have the same mean score. Class A has larger standard deviation. Interpret this.", "Class A scores are more spread out around the mean."),
            Question("Paper 1", 4, "State one advantage of the median over the mean.", "It is less affected by extreme values."),
            Question("Paper 2", 8, "A cumulative frequency graph gives the 25th percentile as 18 and 75th percentile as 32. Estimate the IQR and interpret it.", "IQR $14$; middle 50% of values span about 14 units."),
            Question("Paper 1", 5, "A data set has mean 15. A value 25 is added to 9 existing values. Find the new mean.", "Old total $135$, new total $160$, new mean $16$."),
        ],
    },
    {
        "n": 7,
        "title": "Modelling Relationships Between Two Data Sets: Statistics for Bivariate Data",
        "subtitle": "Scatter diagrams, correlation, line of best fit, least squares regression, and residuals",
        "toc": [
            "7.1 Scatter diagrams",
            "7.2 Measuring correlation",
            "7.3 The line of best fit",
            "7.4 Least squares regression",
        ],
        "syllabus": [
            "Use scatter diagrams to describe association between two variables.",
            "Interpret correlation strength, direction, and limitations.",
            "Use linear regression for prediction and explain extrapolation risk.",
            "Interpret residuals and reason about model suitability.",
        ],
        "source_html": [
            "hs-G13-correlation-and-regression.html",
            "hs-G14-regression-inference-and-rank-correlation.html",
            "hs-G15-bivariate-data-time-series-and-forecasting.html",
        ],
        "learn": [
            ("Scatter diagram", "A scatter diagram reveals direction, form, strength, and outliers."),
            ("Correlation", "$r$ measures linear association only; it does not prove causation."),
            ("Regression", "A least-squares line has the form $y=a+bx$ and is used for prediction within the data range."),
            ("Residual", "Residual = observed value - predicted value. Patterns in residuals warn that the model may be unsuitable."),
        ],
        "worked": [
            ("Prediction", "If $\\hat y=12+0.8x$, then at $x=25$, predicted $y=32$."),
            ("Residual", "If observed $y=35$ and predicted $y=32$, residual is $3$."),
        ],
        "questions": [
            Question("Paper 1", 4, "A data set has $r=-0.91$. Describe the correlation.", "Strong negative linear correlation."),
            Question("Paper 2", 5, "A regression line is $\\hat y=5.4+1.8x$. Predict $y$ when $x=12$.", "$27.0$."),
            Question("Paper 2", 6, "The observed value is 30 and the predicted value is 27.4. Find and interpret the residual.", "Residual $2.6$; observed is 2.6 above prediction."),
            Question("Paper 1", 4, "Explain why correlation does not imply causation.", "A third variable or coincidence may explain the association."),
            Question("Paper 2", 7, "A model from ages 12 to 18 is used to predict at age 30. Name the issue.", "Extrapolation beyond the data range."),
            Question("Paper 1", 5, "State which variable is usually plotted on the horizontal axis in a regression context.", "The explanatory/independent variable."),
            Question("Paper 2", 8, "A residual plot curves upward. What does this suggest about a linear model?", "A linear model may be inappropriate; consider a nonlinear model."),
            Question("Paper 1", 5, "If $r=0.04$, what can be said about linear relationship?", "Very weak or no linear correlation."),
        ],
    },
    {
        "n": 8,
        "title": "Quantifying Randomness: Probability",
        "subtitle": "Theoretical and experimental probability, Venn diagrams, sample spaces, independent/dependent events, and tree diagrams",
        "toc": [
            "8.1 Theoretical and experimental probability",
            "8.2 Venn diagrams and sample spaces",
            "8.3 Independent and dependent events and conditional probability",
            "8.4 Probability tree diagrams",
        ],
        "syllabus": [
            "Use set notation, Venn diagrams, and sample spaces for probability.",
            "Calculate combined, conditional, independent, and dependent probabilities.",
            "Use tree diagrams for multi-stage experiments.",
            "Connect experimental probability, simulation, and long-run relative frequency.",
        ],
        "source_html": [
            "hs-G1-counting-and-combinatorics.html",
            "hs-G2-probability-conditional-and-bayes.html",
            "hs-G17-statistical-computing-and-simulation.html",
        ],
        "learn": [
            ("Probability scale", "Probabilities lie from 0 to 1 and describe long-run expectation or theoretical likelihood."),
            ("Venn diagrams", "Use regions carefully; subtract intersections when counting unions."),
            ("Conditional probability", "$P(A|B)=\\frac{P(A\\cap B)}{P(B)}$ when $P(B)>0$."),
            ("Independence", "Events are independent when $P(A\\cap B)=P(A)P(B)$, or equivalently $P(A|B)=P(A)$."),
        ],
        "worked": [
            ("Union", "If $P(A)=0.45$, $P(B)=0.30$, and $P(A\\cap B)=0.12$, then $P(A\\cup B)=0.63$."),
            ("Conditional", "If $P(A\\cap B)=0.18$ and $P(B)=0.60$, then $P(A|B)=0.30$."),
        ],
        "questions": [
            Question("Paper 1", 5, "Given $P(A)=0.6$, $P(B)=0.35$, and $P(A\\cap B)=0.2$, find $P(A\\cup B)$.", "$0.75$."),
            Question("Paper 1", 4, "If $P(A\\cap B)=0.12$ and $P(B)=0.40$, find $P(A|B)$.", "$0.30$."),
            Question("Paper 1", 5, "Events $A$ and $B$ have $P(A)=0.5$, $P(B)=0.3$, $P(A\\cap B)=0.15$. Are they independent?", "Yes, because $0.5(0.3)=0.15$."),
            Question("Paper 2", 6, "A bag has 4 red and 6 blue balls. Two balls are chosen without replacement. Find probability both are red.", "$\\frac4{10}\\cdot\\frac39=\\frac2{15}$."),
            Question("Paper 2", 7, "A test has sensitivity 0.95 and false positive rate 0.04. Disease prevalence is 0.10. Find probability of a positive test.", "$0.95(0.10)+0.04(0.90)=0.131$."),
            Question("Paper 1", 4, "State the complement rule for an event $A$.", "$P(A')=1-P(A)$."),
            Question("Paper 2", 8, "In a survey of 80 students, 50 study physics, 36 study chemistry, and 22 study both. Find how many study neither.", "$50+36-22=64$ study at least one, so 16 neither."),
            Question("Paper 1", 5, "A fair die is rolled twice. Find probability of two sixes.", "$\\frac1{36}$."),
        ],
    },
    {
        "n": 9,
        "title": "Representing Equivalent Quantities: Exponentials and Logarithms",
        "subtitle": "Exponent laws, logarithms, exponential models, and derivatives of exponential and logarithmic functions",
        "toc": [
            "9.1 Exponents",
            "9.2 Logarithms",
            "9.3 Derivatives of exponential functions and the natural logarithmic function",
        ],
        "syllabus": [
            "Use exponent and logarithm laws in exact and applied contexts.",
            "Solve exponential and logarithmic equations within the SL scope.",
            "Model growth and decay using exponential functions.",
            "Differentiate $e^x$, $a^x$, and $\\ln x$ where required.",
        ],
        "source_html": [
            "hs-B6-exponential-and-logarithmic-functions.html",
            "hs-E3-differentiation-techniques.html",
            "hs-J1-interest-and-investments.html",
        ],
        "learn": [
            ("Inverse relationship", "Logarithms answer exponent questions: $a^x=b$ means $x=\\log_a b$."),
            ("Natural base", "$e$ is central to continuous growth and calculus."),
            ("Growth/decay", "Models often have the form $N(t)=N_0a^t$ or $N(t)=N_0e^{kt}$."),
            ("Calculus link", "$\\frac{d}{dx}e^x=e^x$ and $\\frac{d}{dx}\\ln x=\\frac1x$ for $x>0$."),
        ],
        "worked": [
            ("Solving exponential", "$3(1.08)^t=6$ gives $(1.08)^t=2$, so $t=\\frac{\\ln2}{\\ln1.08}\\approx9.01$."),
            ("Derivative", "If $f(x)=5e^{2x}$, then $f'(x)=10e^{2x}$."),
        ],
        "questions": [
            Question("Paper 1", 5, "Solve $2e^{3x}=10$.", "$x=\\frac{\\ln5}{3}$."),
            Question("Paper 1", 4, "Simplify $\\log_2 32$.", "$5$."),
            Question("Paper 1", 5, "Use log laws to write $\\ln x+2\\ln y$ as one logarithm.", "$\\ln(xy^2)$."),
            Question("Paper 2", 7, "A population is $P=1200(1.035)^t$. Find when it first exceeds 1800.", "$t>\\frac{\\ln1.5}{\\ln1.035}\\approx11.8$, so after 12 years."),
            Question("Paper 1", 5, "Differentiate $f(x)=4e^x-3\\ln x$.", "$f'(x)=4e^x-\\frac3x$."),
            Question("Paper 1", 6, "Solve $\\ln(x-1)=2$.", "$x=1+e^2$."),
            Question("Paper 2", 8, "A value halves every 6 years. Write an exponential model for initial value 500.", "$V(t)=500(0.5)^{t/6}$."),
            Question("Paper 1", 5, "Find the gradient of $y=e^{2x}$ at $x=0$.", "$y'=2e^{2x}$, gradient $2$."),
        ],
    },
    {
        "n": 10,
        "title": "From Approximation to Generalization: Integration",
        "subtitle": "Antiderivatives, indefinite integrals, definite integrals, the fundamental theorem, and area",
        "toc": [
            "10.1 Antiderivatives and the indefinite integral",
            "10.2 More on indefinite integrals",
            "10.3 Area and definite integrals",
            "10.4 Fundamental theorem of calculus",
            "10.5 Area between two curves",
        ],
        "syllabus": [
            "Find antiderivatives and include the constant of integration.",
            "Evaluate definite integrals using the fundamental theorem of calculus.",
            "Interpret areas under and between curves.",
            "Use numerical or technology-supported integration when appropriate.",
        ],
        "source_html": [
            "hs-E7-introduction-to-integration.html",
            "hs-E8-integration-techniques.html",
            "hs-E9-applications-of-integration.html",
        ],
        "learn": [
            ("Antiderivative", "Integration reverses differentiation. A family of antiderivatives differs by a constant."),
            ("Definite integral", "$\\int_a^b f(x)\\,dx=F(b)-F(a)$ when $F'(x)=f(x)$."),
            ("Area", "Area is non-negative, while a definite integral can be negative if the graph is below the axis."),
            ("Between curves", "Area between curves uses top minus bottom across the interval."),
        ],
        "worked": [
            ("Indefinite integral", "$\\int(6x^2-4x+1)dx=2x^3-2x^2+x+C$."),
            ("Definite integral", "$\\int_0^2(3x^2+1)dx=[x^3+x]_0^2=10$."),
        ],
        "questions": [
            Question("Paper 1", 5, "Find $\\int(4x^3-6x+2)dx$.", "$x^4-3x^2+2x+C$."),
            Question("Paper 1", 5, "Evaluate $\\int_1^3 2x\\,dx$.", "$[x^2]_1^3=8$."),
            Question("Paper 1", 6, "Given $f'(x)=6x-4$ and $f(2)=9$, find $f(x)$.", "$f(x)=3x^2-4x+5$."),
            Question("Paper 2", 7, "Find the area under $y=x^2+1$ from $x=0$ to $x=3$.", "$\\int_0^3(x^2+1)dx=12$."),
            Question("Paper 1", 6, "Find the area between $y=4$ and $y=x^2$ from $x=0$ to $x=2$.", "$\\int_0^2(4-x^2)dx=\\frac{16}{3}$."),
            Question("Paper 2", 7, "Velocity is $v(t)=3t^2-2t$ for $0\\le t\\le4$. Find displacement.", "$\\int_0^4(3t^2-2t)dt=48-16=32$."),
            Question("Paper 1", 5, "Explain why $\\int_{-1}^{1}x\\,dx=0$ is not the total area.", "Positive and negative signed areas cancel."),
            Question("Paper 2", 8, "Use trapezoidal rule with ordinates 2, 3, 5, 6 and spacing 1 to estimate area.", "$\\frac12(2+2(3+5)+6)=12$."),
        ],
    },
    {
        "n": 11,
        "title": "Relationships in Space: Geometry and Trigonometry in 2D and 3D",
        "subtitle": "Geometry, right-angled trigonometry, sine rule, cosine rule, and applications",
        "toc": [
            "11.1 The geometry of 3D shapes",
            "11.2 Right-angled triangle trigonometry",
            "11.3 The sine rule",
            "11.4 The cosine rule",
            "11.5 Applications of right and non-right-angled trigonometry",
        ],
        "syllabus": [
            "Use geometry and trigonometry to solve 2D and 3D problems.",
            "Use sine rule, cosine rule, and triangle area formula.",
            "Apply right-triangle trigonometry to bearings, elevation, and spatial contexts.",
            "Use appropriate units and diagrams to communicate modelling assumptions.",
        ],
        "source_html": [
            "hs-C1-triangle-trigonometry-bearings-3d.html",
            "hs-D7-solid-geometry-stereometry.html",
            "hs-D1-coordinate-geometry.html",
        ],
        "learn": [
            ("Right triangles", "Use sine, cosine, and tangent ratios when a right angle is present."),
            ("Sine rule", "$\\frac a{\\sin A}=\\frac b{\\sin B}=\\frac c{\\sin C}$ for non-right triangles."),
            ("Cosine rule", "$c^2=a^2+b^2-2ab\\cos C$ generalizes Pythagoras."),
            ("3D thinking", "Draw a clear 2D triangle inside the 3D situation before calculating."),
        ],
        "worked": [
            ("Cosine rule", "With sides 7, 9 and included angle $60^\\circ$, third side squared is $49+81-126(0.5)=67$, so side is $\\sqrt{67}$."),
            ("Bearing", "Bearings are measured clockwise from north and written with three digits, such as $048^\\circ$."),
        ],
        "questions": [
            Question("Paper 1", 5, "In a right triangle, opposite side is 7 and hypotenuse is 12. Find the angle.", "$\\theta=\\sin^{-1}(7/12)\\approx35.7^\\circ$."),
            Question("Paper 1", 6, "Use the cosine rule to find the third side when $a=6$, $b=10$, and included angle $50^\\circ$.", "$c^2=6^2+10^2-2(6)(10)\\cos50^\\circ$, $c\\approx7.67$."),
            Question("Paper 1", 5, "Find the area of a triangle with sides 8 and 11 and included angle $35^\\circ$.", "$\\frac12(8)(11)\\sin35^\\circ\\approx25.2$."),
            Question("Paper 2", 7, "A ladder 5 m long reaches a wall at angle $68^\\circ$ to the ground. Find the height reached.", "$5\\sin68^\\circ\\approx4.64$ m."),
            Question("Paper 2", 8, "Two points are $A(1,2,3)$ and $B(5,4,1)$. Find $AB$.", "$\\sqrt{4^2+2^2+(-2)^2}=\\sqrt{24}=2\\sqrt6$."),
            Question("Paper 1", 4, "State the sine rule.", "$\\frac a{\\sin A}=\\frac b{\\sin B}=\\frac c{\\sin C}$."),
            Question("Paper 2", 7, "A ship sails 12 km on bearing 040 then 9 km on bearing 130. Find the included angle for the displacement triangle.", "The change in direction is $90^\\circ$, so included angle is $90^\\circ$."),
            Question("Paper 1", 5, "Find the volume of a cylinder with radius 3 and height 8.", "$72\\pi$."),
        ],
    },
    {
        "n": 12,
        "title": "Periodic Relationships: Trigonometric Functions",
        "subtitle": "Radians, arcs, sectors, unit circle, identities, equations, and trigonometric functions",
        "toc": [
            "12.1 Radian measure, arcs, sectors and segments",
            "12.2 Trigonometric ratios in the unit circle",
            "12.3 Trigonometric identities and equations",
            "12.4 Trigonometric functions",
        ],
        "syllabus": [
            "Use radians, arc length, and sector area.",
            "Use the unit circle to understand exact values and periodicity.",
            "Apply core trigonometric identities and solve equations in intervals.",
            "Interpret amplitude, period, phase shift, and vertical shift of trigonometric models.",
        ],
        "source_html": [
            "hs-C2-radian-measure-unit-circle-graphs.html",
            "hs-C3-trigonometric-identities.html",
            "hs-C4-trigonometric-equations.html",
            "hs-C5-trigonometric-modelling-harmonic-motion.html",
        ],
        "learn": [
            ("Radians", "Radians measure angle by arc length over radius: $\\theta=s/r$."),
            ("Unit circle", "Coordinates on the unit circle are $(\\cos\\theta,\\sin\\theta)$."),
            ("Identities", "$\\sin^2\\theta+\\cos^2\\theta=1$ connects the trigonometric functions."),
            ("Models", "$a\\sin(b(x-c))+d$ has amplitude $|a|$, period $\\frac{2\\pi}{|b|}$, and midline $y=d$."),
        ],
        "worked": [
            ("Arc length", "For radius 5 and angle 1.2 radians, arc length is $s=r\\theta=6$."),
            ("Period", "For $y=3\\sin(2x)+1$, amplitude is 3, period is $\\pi$, midline is $y=1$."),
        ],
        "questions": [
            Question("Paper 1", 4, "Convert $150^\\circ$ to radians.", "$\\frac{5\\pi}{6}$."),
            Question("Paper 1", 5, "Find arc length for radius 8 and angle $\\frac{3\\pi}{4}$.", "$6\\pi$."),
            Question("Paper 1", 5, "Find sector area for radius 6 and angle 1.5 radians.", "$\\frac12(36)(1.5)=27$."),
            Question("Paper 1", 5, "Solve $\\sin x=\\frac12$ for $0\\le x\\le2\\pi$.", "$x=\\frac\\pi6,\\frac{5\\pi}{6}$."),
            Question("Paper 2", 7, "For $y=4\\cos(3x)-2$, state amplitude, period, and midline.", "Amplitude 4, period $\\frac{2\\pi}{3}$, midline $y=-2$."),
            Question("Paper 1", 5, "Use an identity to simplify $1-\\sin^2x$.", "$\\cos^2x$."),
            Question("Paper 2", 8, "A tide height is $h=2.1\\sin(\\frac\\pi6 t)+3.4$. Find period and maximum height.", "Period 12 hours; max height 5.5."),
            Question("Paper 1", 6, "Solve $2\\cos x-1=0$ for $0\\le x\\le2\\pi$.", "$x=\\frac\\pi3,\\frac{5\\pi}{3}$."),
        ],
    },
    {
        "n": 13,
        "title": "Modelling Change: More Calculus",
        "subtitle": "Derivatives with sine and cosine, applications, integration by substitution, and kinematics",
        "toc": [
            "13.1 Derivatives with sine and cosine",
            "13.2 Applications of derivatives",
            "13.3 Integration with sine, cosine and substitution",
            "13.4 Kinematics and accumulating change",
        ],
        "syllabus": [
            "Differentiate and integrate sine and cosine functions within SL expectations.",
            "Use calculus to model rates, optimization, and motion.",
            "Use substitution in accessible integrals.",
            "Connect displacement, velocity, acceleration, and accumulated change.",
        ],
        "source_html": [
            "hs-E3-differentiation-techniques.html",
            "hs-E4-related-rates.html",
            "hs-E5-curve-sketching-and-optimisation.html",
            "hs-E7-introduction-to-integration.html",
            "hs-I2-kinematics-with-calculus.html",
        ],
        "learn": [
            ("Trig derivatives", "$\\frac d{dx}\\sin x=\\cos x$ and $\\frac d{dx}\\cos x=-\\sin x$ when $x$ is in radians."),
            ("Chain rule feel", "For simple composites, multiply by the derivative of the inside function."),
            ("Substitution", "Substitution reverses the chain rule."),
            ("Kinematics", "Velocity is derivative of displacement; displacement is integral of velocity."),
        ],
        "worked": [
            ("Trig gradient", "If $f(x)=3\\sin(2x)$, then $f'(x)=6\\cos(2x)$."),
            ("Accumulation", "If $v(t)=4t-1$, displacement from 0 to 3 is $\\int_0^3(4t-1)dt=15$."),
        ],
        "questions": [
            Question("Paper 1", 5, "Differentiate $f(x)=5\\sin x-2\\cos x$.", "$f'(x)=5\\cos x+2\\sin x$."),
            Question("Paper 1", 5, "Differentiate $g(x)=\\sin(3x)$.", "$g'(x)=3\\cos(3x)$."),
            Question("Paper 1", 6, "Evaluate $\\int_0^{\\pi/2}\\cos x\\,dx$.", "$1$."),
            Question("Paper 1", 6, "Find $\\int 4\\cos(2x)dx$.", "$2\\sin(2x)+C$."),
            Question("Paper 2", 8, "Velocity is $v(t)=6\\cos(2t)$. Find displacement from $0$ to $\\pi/4$.", "$\\int_0^{\\pi/4}6\\cos(2t)dt=3$."),
            Question("Paper 1", 6, "For $s(t)=t^3-9t^2+15t$, find acceleration.", "$v=3t^2-18t+15$, $a=6t-18$."),
            Question("Paper 2", 7, "Find stationary points of $f(x)=\\sin x$ on $0\\le x\\le2\\pi$.", "$f'(x)=\\cos x=0$, so $x=\\pi/2,3\\pi/2$."),
            Question("Paper 1", 5, "Use substitution idea to find $\\int 2x(x^2+1)^3dx$.", "$\\frac14(x^2+1)^4+C$."),
        ],
    },
    {
        "n": 14,
        "title": "Valid Comparisons and Informed Decisions: Probability Distributions",
        "subtitle": "Random variables, binomial distribution, normal distribution, and decision making",
        "toc": [
            "14.1 Random variables",
            "14.2 The binomial distribution",
            "14.3 The normal distribution",
        ],
        "syllabus": [
            "Work with discrete random variables and probability distributions.",
            "Use expected value and variance to interpret long-run behaviour.",
            "Use binomial and normal distributions in context.",
            "Use technology to calculate distribution probabilities and inverse normal values.",
        ],
        "source_html": [
            "hs-G3-discrete-random-variables.html",
            "hs-G4-binomial-distribution.html",
            "hs-G6-continuous-random-variables.html",
            "hs-G7-the-normal-distribution.html",
            "hs-G8-sampling-distributions-and-clt.html",
        ],
        "learn": [
            ("Random variable", "A random variable assigns numerical values to outcomes."),
            ("Expected value", "$E(X)=\\sum xp(x)$ for a discrete random variable."),
            ("Binomial", "$X\\sim B(n,p)$ when there are fixed independent trials with two outcomes and constant success probability."),
            ("Normal", "$X\\sim N(\\mu,\\sigma^2)$ is continuous; probabilities are areas under the bell curve."),
        ],
        "worked": [
            ("Expected value", "If $X$ takes 0, 1, 2 with probabilities 0.2, 0.5, 0.3, then $E(X)=0(0.2)+1(0.5)+2(0.3)=1.1$."),
            ("Binomial", "If $X\\sim B(8,0.3)$, then $P(X=2)=\\binom82(0.3)^2(0.7)^6\\approx0.296$."),
        ],
        "questions": [
            Question("Paper 1", 5, "A random variable has $P(X=0)=0.2$, $P(X=1)=0.5$, $P(X=2)=0.3$. Find $E(X)$.", "$1.1$."),
            Question("Paper 1", 5, "For $X\\sim B(10,0.4)$, find $P(X=3)$.", "$\\binom{10}{3}(0.4)^3(0.6)^7\\approx0.215$."),
            Question("Paper 2", 6, "For $X\\sim B(20,0.15)$, state the mean and variance.", "Mean $3$; variance $20(0.15)(0.85)=2.55$."),
            Question("Paper 2", 7, "Let $Y\\sim N(50,8^2)$. Find $P(Y<58)$.", "$z=1$, probability $\\approx0.8413$."),
            Question("Paper 2", 8, "Scores are normally distributed with mean 70 and sd 6. Find the score exceeded by the top 10%.", "$x=70+1.2816(6)\\approx77.7$."),
            Question("Paper 1", 4, "State two conditions for a binomial model.", "Fixed number of independent trials; constant success probability; two outcomes."),
            Question("Paper 2", 7, "For $X\\sim B(5,0.2)$, find $P(X\\ge1)$.", "$1-P(X=0)=1-0.8^5\\approx0.672$."),
            Question("Paper 2", 8, "A machine fills bottles with $N(500,4^2)$ ml. Find probability a bottle has between 496 and 508 ml.", "$z=-1$ to $2$, probability $\\approx0.8186$."),
        ],
    },
]


def extract_template_parts() -> dict[str, str]:
    with ZipFile(ZIP_PATH) as zf:
        sample = zf.read(SAMPLE_HTML).decode("utf-8")

    head_links = "\n".join(
        m.group(0)
        for m in re.finditer(r"<link[^>]+>|<script[^>]+src=[^>]+></script>", sample, flags=re.I)
        if "icon" in m.group(0) or "fonts.googleapis" in m.group(0) or "fonts.gstatic" in m.group(0) or "KaTeX" in m.group(0) or "katex" in m.group(0)
    )
    base_style = re.search(r"<style>([\s\S]*?)</style>", sample).group(1)
    header = re.search(r"<header[\s\S]*?</header>", sample).group(0)
    footer = re.search(r"<footer[\s\S]*?</footer>", sample).group(0)
    return {"head_links": head_links, "base_style": base_style, "header": header, "footer": footer}


def render_list(items: list[str], class_name: str = "flowlist") -> str:
    return f"<ul class=\"{class_name}\">" + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"


def render_toc(items: list[str]) -> str:
    return "<div class=\"grid2\">" + "".join(
        f"<div class=\"card slim\"><span class=\"sectlabel\">Topic</span><p>{esc(item)}</p></div>"
        for item in items
    ) + "</div>"


def render_learn(items: list[tuple[str, str]]) -> str:
    return "".join(
        f"""
        <div class="card glow">
          <h3>{esc(title)}</h3>
          <p>{esc(body)}</p>
        </div>
        """
        for title, body in items
    )


def render_worked(items: list[tuple[str, str]]) -> str:
    return "".join(
        f"""
        <details class="ex">
          <summary><span class="badge">AASL</span><span class="extitle">{esc(title)}</span><span class="lvl">Worked</span><span class="chev">›</span></summary>
          <div class="exbody">
            <div class="step"><span class="st">Method</span><p>{esc(body)}</p></div>
          </div>
        </details>
        """
        for title, body in items
    )


def render_questions(items: list[Question]) -> str:
    cards = []
    for i, q in enumerate(items, 1):
        cards.append(
            f"""
            <article class="qcard exam-card" data-q="{i}">
              <div class="qhead">
                <span class="qtype">{esc(q.mode)}</span>
                <span class="pracmeta"><b>Question {i}</b> · [{q.marks} marks]</span>
              </div>
              <p>{esc(q.prompt)}</p>
              <button class="btn ghost reveal" type="button">Show answer</button>
              <div class="answerline hidden"><span class="lab">Answer</span>{esc(q.answer)}</div>
            </article>
            """
        )
    return "\n".join(cards)


def render_sources(chapter: dict) -> str:
    n = chapter["n"]
    teacher = "402104_bks_MaaSL_12uu_tn00_xxaann_updated.pdf" if n == 12 else f"bks_MaaSL_{n:02d}uu_tn00_xxaann.pdf"
    test = f"bks_MaaSL_{n:02d}uu_ct00_xxaann.pdf"
    exercises = sorted((ROOT / "Exercises").glob(f"bks_MaaSL_{n:02d}*.pdf"))
    exercise_names = [p.name for p in exercises]
    source_bits = [
        ("Teacher notes", teacher),
        ("Chapter test", test),
        ("Oxford ToC", "IBDP Math AASL Oxford ToC.pdf"),
        ("Specimen style reference", "AA SL specimen papers in dp-mathematics-analysis-and-approaches-specimen-papers-en.pdf"),
    ]
    source_bits.extend(("High-school HTML", name) for name in chapter["source_html"])
    source_bits.extend(("Exercise PDF", name) for name in exercise_names[:8])
    if len(exercise_names) > 8:
        source_bits.append(("Exercise PDF", f"+{len(exercise_names)-8} more chapter exercise files"))
    return "".join(
        f"<span class=\"sourcechip\"><b>{esc(kind)}</b>{esc(name)}</span>"
        for kind, name in source_bits
    )


def nfmt(value: float) -> str:
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    if abs(value) >= 100:
        return f"{value:.1f}"
    return f"{value:.3g}"


def steps(*items: str) -> str:
    return "||".join(items)


def qq(mode: str, marks: int, prompt: str, answer: str, solution: str, visual: str = "") -> Question:
    return Question(mode, marks, prompt, answer, solution, visual)


def make_exam_questions(chapter: dict) -> list[Question]:
    n = chapter["n"]
    out: list[Question] = []
    for k in range(QUESTIONS_PER_CHAPTER):
        t = k % 10
        c = k // 10
        if n == 1:
            a = 5 + c
            d = 2 + (c % 5)
            r = 0.62 + 0.03 * (c % 5)
            if t == 0:
                m = 12 + c
                u = a + (m - 1) * d
                s = m * (2 * a + (m - 1) * d) / 2
                out.append(qq("Paper 1", 6, f"An arithmetic sequence has first term {a} and common difference {d}. Find $u_{m}$ and $S_{m}$.", f"$u_{m}={nfmt(u)}$, $S_{m}={nfmt(s)}$.", steps("Use $u_n=u_1+(n-1)d$.", f"Substitute: $u_{m}={a}+({m}-1)({d})={nfmt(u)}$.", "Use $S_n=n(2u_1+(n-1)d)/2$.", f"$S_{m}={m}(2({a})+({m}-1)({d}))/2={nfmt(s)}$."), "sequence"))
            elif t == 1:
                m = 6 + c
                u = a * (1.2 + 0.05 * c) ** (m - 1)
                ratio = 1.2 + 0.05 * c
                out.append(qq("Paper 1", 5, f"A geometric sequence has first term {a} and common ratio {nfmt(ratio)}. Find $u_{m}$.", f"$u_{m}={nfmt(u)}$.", steps("Use $u_n=u_1r^(n-1)$.", f"Substitute $u_{m}={a}({nfmt(ratio)})^({m}-1)$.", f"Evaluate to obtain {nfmt(u)}."), "sequence"))
            elif t == 2:
                inf = a / (1 - r)
                out.append(qq("Paper 2", 6, f"A bouncing ball rises to {int(r*100)}% of its previous height after each bounce. Its first rebound is {a} m. Find the total upward rebound distance.", f"{nfmt(inf)} m.", steps("The rebound heights form a geometric series.", f"The first term is {a} and the common ratio is {nfmt(r)}.", "Since the ratio is between -1 and 1, use $S_infinity=a/(1-r)$.", f"$S={a}/(1-{nfmt(r)})={nfmt(inf)}$ m."), "sequence"))
            elif t == 3:
                x = 1 + c
                coeff = math.comb(6, 2) * (2 ** 2) * (x ** 2)
                out.append(qq("Paper 1", 5, f"Find the coefficient of $x^2$ in $(1+{2+c%3}x)^6$.", f"{math.comb(6,2)*(2+c%3)**2}.", steps("Use the binomial term $C(6,2)(kx)^2$.", f"Here $k={2+c%3}$.", f"The coefficient is $15({2+c%3})^2={math.comb(6,2)*(2+c%3)**2}$."), "bar"))
            elif t == 4:
                m = 20 + c
                total = sum(3 * i - 1 for i in range(1, m + 1))
                out.append(qq("Paper 1", 6, f"Evaluate $sum_(i=1)^{m}(3i-1)$.", f"{total}.", steps("Separate the sum into $3 sum i - sum 1$.", f"$sum_(i=1)^{m} i={m}({m}+1)/2$.", f"So the sum is $3({m}({m}+1)/2)-{m}={total}$."), "bar"))
            elif t == 5:
                p = 800 + 100 * c
                dep = 0.82 - 0.01 * (c % 3)
                val = p * (dep ** 5)
                out.append(qq("Paper 2", 7, f"A laptop costs {p} BHD and loses {int((1-dep)*100)}% of its value each year. Model its value after 5 years.", f"{nfmt(val)} BHD.", steps("Depreciation is geometric decay.", f"The yearly multiplier is {nfmt(dep)}.", f"$V= {p}({nfmt(dep)})^5={nfmt(val)}$ BHD."), "curve"))
            elif t == 6:
                m = 10 + c
                out.append(qq("Paper 1", 5, f"The first three terms are {a}, {a+d}, {a+2*d}. Find the common difference and the {m}th term.", f"$d={d}$, $u_{m}={a+(m-1)*d}$.", steps("Subtract consecutive terms to find the common difference.", f"$d={a+d}-{a}={d}$.", "Use the arithmetic formula.", f"$u_{m}={a}+({m}-1){d}={a+(m-1)*d}$."), "sequence"))
            elif t == 7:
                rate = 40 + 5 * c
                months = 12 + c
                g = 1.004 + 0.001 * (c % 3)
                s = rate * (g ** months - 1) / (g - 1)
                out.append(qq("Paper 2", 8, f"A student saves {rate} BHD each month. The monthly growth factor is {nfmt(g)}. Find the value after {months} end-of-month deposits.", f"{nfmt(s)} BHD.", steps("This is a finite geometric sum.", f"$S={rate}(1+{nfmt(g)}+...+{nfmt(g)}^{months-1})$.", f"$S={rate}(({nfmt(g)})^{months}-1)/({nfmt(g)}-1)$.", f"Evaluate: {nfmt(s)} BHD."), "sequence"))
            elif t == 8:
                out.append(qq("Graphical", 6, "Use the graph of the generated sequence tool. Describe how changing the common difference changes the shape of the plotted terms.", "The points remain on a straight line; the gradient changes.", steps("Arithmetic sequences have constant first difference.", "A constant first difference produces points on a straight line when term number is plotted horizontally.", "Increasing the common difference makes the line steeper; decreasing it makes the line flatter or negative."), "sequence"))
            else:
                out.append(qq("Paper 1", 5, f"An infinite geometric series has first term {a} and sum {5*a}. Find the common ratio.", f"$r={nfmt(0.8)}$.", steps("Use $S_infinity=a/(1-r)$.", f"{5*a}={a}/(1-r).", f"1-r={nfmt(a/(5*a))}.", "Therefore $r=0.8$."), "sequence"))
        elif n == 2:
            A = 2 + c
            B = 3 + (c % 5)
            if t == 0:
                out.append(qq("Paper 1", 5, f"For $f(x)={A}x-{B}$ and $g(x)=x^2+{c+1}$, find $(g o f)(x)$.", f"$({A}x-{B})^2+{c+1}$.", steps("Composition means substitute $f(x)$ into $g$.", f"$g(f(x))=({A}x-{B})^2+{c+1}$.", "Expansion is optional unless requested."), "curve"))
            elif t == 1:
                out.append(qq("Paper 1", 4, f"Find the inverse of $f(x)=({A}x-{B})/{B}$.", f"$f^(-1)(x)=({B}x+{B})/{A}$.", steps("Set $y=({A}x-{B})/{B}$.", f"Multiply by {B}: ${B}y={A}x-{B}$.", f"Solve for x: $x=({B}y+{B})/{A}$.", "Replace y with x in the inverse notation."), "mapping"))
            elif t == 2:
                out.append(qq("Paper 1", 4, f"State the domain of $h(x)=sqrt({B*2}-{A}x)$.", f"$x <= {nfmt((B*2)/A)}$.", steps("The expression under a square root must be non-negative.", f"{B*2}-{A}x >= 0.", f"Therefore $x <= {nfmt((B*2)/A)}$."), "curve"))
            elif t == 3:
                out.append(qq("Paper 1", 5, f"The function $p(x)=x^2-{B}$ has domain $x>=0$. State its range and inverse.", f"Range $y>=-{B}$; $p^(-1)(x)=sqrt(x+{B})$.", steps("With domain $x>=0$, the parabola keeps its right branch only.", f"The minimum value is $-{B}$ at x=0.", "For the inverse, swap x and y: $x=y^2-B$.", f"Solve: $y=sqrt(x+{B})$ because the restricted branch is non-negative."), "curve"))
            elif t == 4:
                out.append(qq("Paper 2", 6, f"A taxi fare is modelled by $C(d)={nfmt(1.1+0.1*c)}d+{B}$. Interpret the gradient and intercept.", f"Gradient: {nfmt(1.1+0.1*c)} BHD/km; intercept: {B} BHD fixed charge.", steps("In a linear model, the gradient is the change in cost per kilometre.", "The vertical intercept is the cost when distance is 0.", "State both with units and context."), "line"))
            elif t == 5:
                out.append(qq("Paper 1", 5, f"If $(f o g)(x)={A}x+{B}$ and $g(x)=x-{c+1}$, find one possible $f(x)$.", f"$f(x)={A}x+{B + A*(c+1)}$.", steps("Let the input to f be u=g(x)=x-k.", "Then x=u+k.", f"Substitute into {A}x+{B}.", f"$f(u)={A}(u+{c+1})+{B}={A}u+{B + A*(c+1)}$."), "mapping"))
            elif t == 6:
                out.append(qq("Graphical", 6, "The graph window shows only part of a function. Explain why the visible interval is not necessarily the domain.", "A graph window is a viewing choice; the mathematical rule and restrictions determine the domain.", steps("A screen window hides values outside the chosen x-range.", "The actual domain comes from the function definition and any restrictions.", "For example, a denominator cannot be zero even if that value is off-screen."), "curve"))
            elif t == 7:
                out.append(qq("Paper 1", 6, f"Solve $f^(-1)(a)={B}$ for $a$ when $f(x)={A}x+{c}$.", f"$a={A*B+c}$.", steps("If $f^(-1)(a)=B$, then $a=f(B)$.", f"$a={A}({B})+{c}={A*B+c}$."), "mapping"))
            elif t == 8:
                out.append(qq("Paper 2", 7, f"A function maps temperature in Celsius to Fahrenheit by $F(C)=1.8C+32$. Find the inverse and interpret it.", "$C=(F-32)/1.8$; it converts Fahrenheit to Celsius.", steps("Start with $F=1.8C+32$.", "Subtract 32.", "Divide by 1.8.", "The inverse reverses the original conversion."), "line"))
            else:
                out.append(qq("Paper 1", 5, f"Find the range of $f(x)={A}x+{B}$ for $-2<=x<=4$.", f"$ {B-2*A} <= f(x) <= {4*A+B}$.", steps("A linear function with positive gradient is increasing.", "Evaluate the endpoints of the domain.", f"$f(-2)={B-2*A}$ and $f(4)={4*A+B}$."), "line"))
        else:
            out.append(generic_question(n, k, chapter))
    return out[:QUESTIONS_PER_CHAPTER]


def generic_question(n: int, k: int, chapter: dict) -> Question:
    t = k % 10
    c = k // 10
    title = chapter["title"]
    visual = {
        3: "quadratic", 4: "rational", 5: "derivative", 6: "stats", 7: "scatter",
        8: "probability", 9: "exponential", 10: "integral", 11: "geometry",
        12: "trig", 13: "motion", 14: "distribution",
    }.get(n, "curve")
    if n == 3:
        a = 1 + (c % 3)
        h = c - 3
        k0 = 2 * c - 5
        if t == 0:
            return qq("Paper 1", 5, f"Write $x^2-{2*(c+3)}x+{(c+3)**2-4}$ in completed-square form.", f"$(x-{c+3})^2-4$.", steps("Half the coefficient of x to find the square term.", f"$x^2-{2*(c+3)}x=(x-{c+3})^2-{(c+3)**2}$.", "Combine the constants.", "The completed-square form reveals the vertex."), visual)
        if t == 1:
            return qq("Paper 1", 5, f"Solve ${a}x^2-{a*(5+c)}x+{a*(4+c)}=0$.", "Use factorization or the quadratic formula.", steps("Identify a common factor if possible.", "Use the quadratic formula or factorization.", "State both roots and check by substitution."), visual)
        if t == 2:
            return qq("Graphical", 6, f"The graph of $y={a}(x-{h})^2+{k0}$ is shown. State the vertex and axis of symmetry.", f"Vertex $({h},{k0})$; axis $x={h}$.", steps("Read the transformation form $a(x-h)^2+k$.", "The vertex is $(h,k)$.", "The axis of symmetry is the vertical line through the vertex."), visual)
        if t == 3:
            return qq("Paper 1", 5, f"Find the discriminant of $x^2+{2+c}x+{4+c}$ and state the number of real roots.", "Compute $b^2-4ac$ and classify.", steps("Use $Delta=b^2-4ac$.", "If Delta is positive there are two real roots; zero gives one repeated root; negative gives no real roots.", "Substitute the coefficients and classify."), visual)
        if t == 4:
            return qq("Paper 2", 8, f"A projectile has height $h(t)=-5t^2+{18+c}t+{2+c}$. Find the maximum height.", "Use the vertex.", steps("For $at^2+bt+c$, the vertex occurs at $t=-b/(2a)$.", "Substitute this time into the height function.", "The result is the maximum because the coefficient of $t^2$ is negative."), visual)
        if t == 5:
            return qq("Paper 2", 7, f"A rectangle has perimeter {40+2*c} cm. Express its area in terms of side $x$ and find the maximum area.", "Use $A=x(P/2-x)$, then the vertex.", steps("If one side is x, the adjacent side is P/2 - x.", "Form $A=x(P/2-x)$.", "The maximum occurs at half of P/2, making a square."), visual)
        if t == 6:
            return qq("Paper 1", 5, f"Describe the transformation from $y=x^2$ to $y={a}(x-{h})^2+{k0}$.", "Horizontal shift, vertical stretch/reflection if needed, and vertical shift.", steps("Compare with $a(x-h)^2+k$.", "The value h gives horizontal movement.", "The value k gives vertical movement.", "The value a controls stretch and opening direction."), visual)
        if t == 7:
            return qq("Paper 2", 8, f"Revenue is $R(x)=-2x^2+{44+2*c}x$ and cost is {120+10*c}. Find break-even outputs.", "Solve $R(x)=C$.", steps("Set revenue equal to cost.", "Rearrange into a quadratic equation.", "Solve and interpret only context-valid roots."), visual)
        if t == 8:
            return qq("Graphical", 6, "Use the zoomable graph to determine whether the quadratic has a maximum or minimum and explain using the sign of $a$.", "If $a>0$ it has a minimum; if $a<0$ it has a maximum.", steps("A positive leading coefficient opens upward.", "An upward-opening parabola has a lowest point.", "A negative leading coefficient opens downward and has a highest point."), visual)
        return qq("Paper 1", 5, f"Find the y-intercept of $y={a}x^2+{2+c}x-{5+c}$.", f"$-{5+c}$.", steps("The y-intercept occurs when x=0.", "Substitute x=0 into the expression.", "The constant term is the y-intercept."), visual)
    if n == 4:
        a = 2 + c
        h = c - 2
        v = 1 - c
        prompts = [
            (f"State the asymptotes of $f(x)={a}/(x-{h})+{v}$.", f"$x={h}$ and $y={v}$.", "Read $a/(x-h)+k$: vertical asymptote x=h, horizontal asymptote y=k."),
            (f"Find the domain of $g(x)=({a}x+1)/(x^2-{(c+2)**2})$.", f"$x != {c+2}, -{c+2}$.", "The denominator must not be zero. Factor the difference of squares."),
            (f"Solve $({a}x+1)/(x-1)=4$.", "Solve the resulting linear equation, with x not equal to 1.", "Multiply by the denominator, solve, then check the excluded value."),
            (f"Write $(2x+{5+c})/(x+1)$ in the form $A+B/(x+1)$.", "Divide to reveal the transformed reciprocal form.", "Use algebraic division: make the numerator match a multiple of x+1 plus a remainder."),
            ("Use the graph to explain what happens near the vertical asymptote.", "The function values grow very large positive or negative.", "Approach the asymptote from both sides and describe the end behaviour."),
            (f"Find the x-intercept of $f(x)=({a}x-{2*a})/(x+{c+3})$.", "$x=2$.", "Set the numerator equal to zero, provided the denominator is not zero."),
            (f"A cost model is $C(x)=12+{240+20*c}/x$. Find x when C=20.", f"$x={nfmt((240+20*c)/8)}$.", "Subtract 12, then divide the constant by the remaining cost per item."),
            ("Explain why a rational model may be unsuitable for very small positive x.", "It may predict unrealistic large values near an asymptote.", "Discuss the domain and real-world limitations."),
            ("Use the zoom controls to compare horizontal and vertical asymptotes.", "Vertical asymptotes restrict x; horizontal asymptotes describe end behaviour.", "Zooming out reveals end behaviour while zooming in reveals local behaviour."),
            (f"Transform $y=1/x$ into $y={-a}/(x-{h})+{v}$.", "Reflect/stretch, shift horizontally, then shift vertically.", "Use the parameters in $a/(x-h)+k$."),
        ]
        p, ans, sol = prompts[t]
        return qq("Paper 1" if t < 4 else "Paper 2", 5 + (t % 4), p, ans, steps(sol, "State the final answer in context where appropriate."), visual)
    if n == 5:
        A = 2 + c
        prompts = [
            (f"Differentiate $f(x)={A}x^3-{3+c}x^2+7$.", f"$f'(x)={3*A}x^2-{2*(3+c)}x$.", "Apply the power rule term by term."),
            (f"Find the gradient of $y=x^2+{A}x$ at x={2+c}.", f"{2*(2+c)+A}.", "Differentiate, then substitute the x-value."),
            (f"Find and classify the stationary point of $f(x)=x^2-{2*(4+c)}x+3$.", "Minimum at x equal to half the linear coefficient.", "Solve f'(x)=0 and use f''(x)>0."),
            ("Use the tangent tool to explain the meaning of instantaneous rate of change.", "It is the gradient of the tangent at a point.", "Zoom in on the curve; locally it behaves like the tangent line."),
            (f"Velocity is $v(t)=3t^2-{4+c}t+1$. Find acceleration at t=3.", f"{18-(4+c)}.", "Acceleration is the derivative of velocity; substitute t=3."),
            (f"A profit derivative is $P'(x)=-4x+{32+2*c}$. Find the output for maximum profit.", f"{nfmt((32+2*c)/4)}.", "Set derivative equal to zero and check the derivative changes from positive to negative."),
            (f"Find $f''(x)$ for $f(x)={A}x^4-x^3+5x$.", f"${12*A}x^2-6x$.", "Differentiate twice using the power rule."),
            (f"Determine where $f$ is increasing if $f'(x)=3(x-{1+c%3})(x-{4+c%3})$.", "Outside the two roots.", "Make a sign chart for the derivative."),
            ("Use the derivative graph to identify intervals of increase and decrease.", "f increases where f' is positive and decreases where f' is negative.", "Read the derivative graph relative to the x-axis."),
            (f"Find the tangent line to $y=x^3$ at x={1+c}.", "Use y-y1=m(x-x1).", "Find the point, compute derivative 3x^2, then form the tangent equation."),
        ]
        p, ans, sol = prompts[t]
        return qq("Paper 1" if t < 4 else "Paper 2", 5 + (t % 4), p, ans, steps(sol, "Show substitution because examiner method marks depend on visible working."), visual)
    if n == 6:
        data = [4+c, 7+c, 8+c, 11+c, 20+c]
        mean = sum(data) / len(data)
        prompts = [
            (f"Find the mean of {', '.join(map(str, data))}.", f"{nfmt(mean)}.", "Add all values and divide by the number of values."),
            (f"For a data set with Q1={12+c} and Q3={28+c}, find the IQR and upper outlier fence.", f"IQR=16, upper fence={52+c}.", "IQR=Q3-Q1. Upper fence=Q3+1.5(IQR)."),
            ("A sample is taken by asking only students in the library. Identify the sampling issue.", "Convenience sampling and possible bias.", "Name the method and explain why the sample may not represent the population."),
            ("Use the editable histogram to explain how an outlier affects the mean.", "An outlier pulls the mean toward itself.", "Compare mean and median before and after moving the extreme value."),
            (f"A frequency table has values 1, 2, 3 with frequencies {3+c}, {5+c}, {2+c}. Find the mean.", "Use weighted mean.", "Multiply each value by its frequency, add, then divide by total frequency."),
            ("Two classes have the same mean but different standard deviations. Interpret the larger standard deviation.", "Scores are more spread out.", "Standard deviation measures typical distance from the mean."),
            ("State one advantage of the median over the mean.", "It is less affected by extreme values.", "Explain robustness in context."),
            (f"A data set has mean {15+c}. A new value {25+c} is added to 9 existing values. Find the new mean.", f"{nfmt((9*(15+c)+(25+c))/10)}.", "Recover the old total, add the new value, divide by 10."),
            ("Use the box plot to compare two distributions.", "Compare median, IQR, range, and outliers.", "Make comparative statements, not isolated descriptions."),
            ("Explain when a cumulative frequency graph is useful.", "It estimates medians, quartiles, percentiles, and counts below a value.", "Read values by moving between axes."),
        ]
        p, ans, sol = prompts[t]
        return qq("Paper 1" if t in (0,1,6) else "Paper 2", 4 + (t % 5), p, ans, steps(sol, "Give a contextual sentence where the question asks for interpretation."), visual)
    if n == 7:
        slope = 1.2 + 0.1 * c
        intercept = 4 + c
        prompts = [
            ("A data set has r=-0.91. Describe the correlation.", "Strong negative linear correlation.", "Use both strength and direction."),
            (f"A regression line is $y={intercept}+{nfmt(slope)}x$. Predict y when x=12.", f"{nfmt(intercept+slope*12)}.", "Substitute x=12 into the regression equation."),
            (f"The observed value is {30+c} and predicted value is {27+c}. Find the residual.", "3.", "Residual=observed-predicted."),
            ("Explain why correlation does not imply causation.", "A third variable or coincidence may explain the association.", "Correlation measures association only."),
            ("A model based on ages 12 to 18 is used at age 30. Name the issue.", "Extrapolation.", "Prediction outside the data range is less reliable."),
            ("Use the scatter tool to decide whether a linear model is suitable.", "Look for an approximately straight pattern and random residuals.", "A curve or fan shape suggests another model."),
            ("A residual plot curves upward. What does this suggest?", "A linear model may be inappropriate.", "Residuals should show no pattern for a good linear model."),
            ("If r=0.04, what can be said about linear relationship?", "Very weak or no linear correlation.", "The value is close to zero."),
            (f"Find the x-value predicted to give y={40+c} from $y={intercept}+{nfmt(slope)}x$.", f"{nfmt((40+c-intercept)/slope)}.", "Rearrange the regression equation and solve for x."),
            ("Interpret a positive slope in a regression context.", "As x increases, the predicted y increases.", "State the rate and context if units are provided."),
        ]
        p, ans, sol = prompts[t]
        return qq("Paper 2", 5 + (t % 4), p, ans, steps(sol, "Mention reliability and context for regression conclusions."), visual)
    if n == 8:
        prompts = [
            (f"Given P(A)=0.{5+c%4}, P(B)=0.35, and P(A and B)=0.20, find P(A or B).", "Use P(A)+P(B)-P(A and B).", "Apply the union formula and subtract the overlap once."),
            ("If P(A and B)=0.12 and P(B)=0.40, find P(A|B).", "0.30.", "Use P(A|B)=P(A and B)/P(B)."),
            ("Events A and B have P(A)=0.5, P(B)=0.3, P(A and B)=0.15. Are they independent?", "Yes.", "Check whether P(A)P(B)=P(A and B)."),
            (f"A bag has {4+c} red and {6+c} blue balls. Two balls are chosen without replacement. Find P(both red).", "Use dependent multiplication.", "The second probability changes after the first red is removed."),
            ("A test has sensitivity 0.95, false positive rate 0.04, prevalence 0.10. Find P(positive).", "0.131.", "Add true positives and false positives."),
            ("State the complement rule.", "P(A')=1-P(A).", "The event and complement exhaust the sample space."),
            ("In a survey of 80 students, 50 study physics, 36 chemistry, 22 both. Find neither.", "16.", "Use inclusion-exclusion, then subtract from 80."),
            ("A fair die is rolled twice. Find probability of two sixes.", "1/36.", "Independent events multiply."),
            ("Use the Venn tool to explain mutually exclusive events.", "They have no overlap.", "The intersection is empty, so P(A and B)=0."),
            ("Use a tree diagram to explain dependent events.", "Branch probabilities change after earlier outcomes.", "Update the sample space after each stage."),
        ]
        p, ans, sol = prompts[t]
        return qq("Paper 1" if t < 3 else "Paper 2", 4 + (t % 5), p, ans, steps(sol, "Write probabilities as exact fractions or decimals as requested."), visual)
    if n == 9:
        prompts = [
            (f"Solve $2e^({2+c%3}x)=10$.", "Take natural logs after isolating the exponential.", "Divide by 2, take ln of both sides, then divide by the coefficient of x."),
            ("Simplify log_2 32.", "5.", "Ask: 2 to what power gives 32?"),
            ("Write ln x + 2 ln y as one logarithm.", "ln(xy^2).", "Use the power law and product law."),
            (f"A population is $P=1200(1.{30+c})^t$. Set up the equation for when it exceeds 1800.", "Solve (growth factor)^t > 1.5.", "Divide by 1200 and take logs."),
            ("Differentiate f(x)=4e^x-3ln x.", "4e^x-3/x.", "Differentiate term by term."),
            (f"Solve ln(x-{1+c%3})=2.", f"x={1+c%3}+e^2.", "Rewrite in exponential form."),
            ("A value halves every 6 years. Write a model for initial value 500.", "V=500(0.5)^(t/6).", "Each 6-year interval multiplies by 0.5."),
            ("Find the gradient of y=e^(2x) at x=0.", "2.", "Differentiate using the chain rule, then substitute x=0."),
            ("Use the exponential graph to explain horizontal asymptote.", "The graph approaches but does not cross its baseline.", "Discuss end behaviour from the model."),
            ("Compare exponential and linear growth on the graph.", "Exponential growth has a changing rate; linear growth has constant rate.", "Use gradient behaviour to justify."),
        ]
        p, ans, sol = prompts[t]
        return qq("Paper 1" if t < 3 else "Paper 2", 5 + (t % 4), p, ans, steps(sol, "Use exact logarithmic form unless a decimal is requested."), visual)
    if n == 10:
        prompts = [
            (f"Find the integral of ${4+c}x^3-6x+2$.", "Use the reverse power rule plus C.", "Increase each power by 1 and divide by the new power."),
            (f"Evaluate integral from 1 to 3 of {2+c}x dx.", f"{(2+c)*4}.", "Find an antiderivative and subtract endpoint values."),
            (f"Given f'(x)=6x-{4+c} and f(2)=9, find f(x).", "Integrate then use the condition.", "The constant is found by substituting x=2."),
            ("Find the area under y=x^2+1 from x=0 to x=3.", "12.", "Integrate x^2+1 and evaluate from 0 to 3."),
            ("Find the area between y=4 and y=x^2 from x=0 to x=2.", "16/3.", "Use top minus bottom."),
            (f"Velocity is v(t)=3t^2-{2+c}t. Find displacement from 0 to 4.", "Integrate velocity over time.", "Displacement is signed area under velocity."),
            ("Explain why integral from -1 to 1 of x dx is not total area.", "Signed areas cancel.", "Area must be non-negative on each part."),
            ("Use trapezoidal rule with ordinates 2, 3, 5, 6 and spacing 1.", "12.", "Apply h/2(first+last+2 middle sum)."),
            ("Use the area tool to explain over-estimate and under-estimate rectangles.", "Left/right sums depend on whether the function increases or decreases.", "Compare rectangle heights with the curve."),
            ("Find the area between two curves using technology.", "Graph, find intersections, integrate top minus bottom.", "State limits and expression before evaluating."),
        ]
        p, ans, sol = prompts[t]
        return qq("Paper 1" if t < 4 else "Paper 2", 5 + (t % 4), p, ans, steps(sol, "Include units squared when the context uses measurement."), visual)
    if n == 11:
        prompts = [
            ("In a right triangle, opposite side is 7 and hypotenuse is 12. Find the angle.", "sin^(-1)(7/12).", "Choose sine because opposite and hypotenuse are known."),
            ("Use cosine rule to find the third side when a=6, b=10, included angle 50 degrees.", "About 7.67.", "Substitute into c^2=a^2+b^2-2ab cos C."),
            ("Find area of a triangle with sides 8 and 11 and included angle 35 degrees.", "About 25.2.", "Use area=1/2 ab sin C."),
            ("A ladder 5 m long makes angle 68 degrees with the ground. Find the height reached.", "About 4.64 m.", "Use opposite=hypotenuse sin angle."),
            ("Points are A(1,2,3) and B(5,4,1). Find AB.", "2sqrt(6).", "Use 3D distance formula."),
            ("State the sine rule.", "a/sin A=b/sin B=c/sin C.", "Use it when an opposite side-angle pair is known."),
            ("Use the rotatable 3D viewer to explain why a 2D triangle must be identified inside a solid.", "Calculations happen in a plane inside the 3D object.", "Choose the relevant cross-section first."),
            ("Find volume of a cylinder with radius 3 and height 8.", "72pi.", "Use V=pi r^2 h."),
            ("A bearing is 040 degrees. Explain its meaning.", "40 degrees clockwise from north.", "Bearings are measured clockwise from north with three digits."),
            ("Use the 3D axes to describe the midpoint of A(0,2,4) and B(6,4,8).", "(3,3,6).", "Average each coordinate."),
        ]
        p, ans, sol = prompts[t]
        return qq("Paper 1" if t < 6 else "Paper 2", 5 + (t % 4), p, ans, steps(sol, "Draw or reference a clear diagram before calculating."), visual)
    if n == 12:
        prompts = [
            ("Convert 150 degrees to radians.", "5pi/6.", "Multiply degrees by pi/180."),
            ("Find arc length for radius 8 and angle 3pi/4.", "6pi.", "Use s=r theta."),
            ("Find sector area for radius 6 and angle 1.5 radians.", "27.", "Use A=1/2 r^2 theta."),
            ("Solve sin x=1/2 for 0<=x<=2pi.", "pi/6 and 5pi/6.", "Use unit-circle reference angle and quadrants."),
            ("For y=4cos(3x)-2, state amplitude, period, midline.", "4, 2pi/3, y=-2.", "Compare with a cos(bx)+d."),
            ("Simplify 1-sin^2 x.", "cos^2 x.", "Use sin^2 x+cos^2 x=1."),
            ("A tide height is h=2.1sin(pi t/6)+3.4. Find period and maximum.", "12 hours, 5.5.", "Period=2pi/(pi/6); maximum=midline+amplitude."),
            ("Solve 2cos x-1=0 for 0<=x<=2pi.", "pi/3 and 5pi/3.", "Solve cos x=1/2 and use quadrants I and IV."),
            ("Use the unit-circle tool to explain why sine is positive in quadrants I and II.", "Sine is the y-coordinate.", "The y-coordinate is positive above the x-axis."),
            ("Use the wave graph to explain phase shift.", "It moves the graph horizontally.", "Identify the value c in a sin(b(x-c))+d."),
        ]
        p, ans, sol = prompts[t]
        return qq("Paper 1" if t < 6 else "Paper 2", 5 + (t % 4), p, ans, steps(sol, "Use radians unless the question states degrees."), visual)
    if n == 13:
        prompts = [
            ("Differentiate f(x)=5sin x-2cos x.", "5cos x+2sin x.", "Use d/dx sin x=cos x and d/dx cos x=-sin x."),
            ("Differentiate g(x)=sin(3x).", "3cos(3x).", "Use the chain rule."),
            ("Evaluate integral from 0 to pi/2 of cos x dx.", "1.", "The antiderivative is sin x."),
            ("Find integral of 4cos(2x) dx.", "2sin(2x)+C.", "Reverse the chain rule."),
            ("Velocity is v(t)=6cos(2t). Find displacement from 0 to pi/4.", "3.", "Integrate velocity."),
            ("For s(t)=t^3-9t^2+15t, find acceleration.", "6t-18.", "Differentiate displacement to velocity, then velocity to acceleration."),
            ("Find stationary points of f(x)=sin x on 0<=x<=2pi.", "pi/2 and 3pi/2.", "Solve cos x=0."),
            ("Find integral of 2x(x^2+1)^3 dx.", "(x^2+1)^4/4 + C.", "Use substitution u=x^2+1."),
            ("Use the motion graph to explain when an object changes direction.", "When velocity changes sign.", "Look for zeros of the velocity graph with sign change."),
            ("Use the derivative tool to compare sine and cosine gradients.", "The derivative of sine is cosine.", "At each x, cosine gives the tangent gradient to sine."),
        ]
        p, ans, sol = prompts[t]
        return qq("Paper 1" if t < 5 else "Paper 2", 5 + (t % 4), p, ans, steps(sol, "Show calculus notation clearly for method marks."), visual)
    if n == 14:
        prompts = [
            ("A random variable has P(X=0)=0.2, P(X=1)=0.5, P(X=2)=0.3. Find E(X).", "1.1.", "Multiply each value by its probability and add."),
            ("For X~B(10,0.4), find P(X=3).", "C(10,3)(0.4)^3(0.6)^7.", "Use the binomial probability formula."),
            ("For X~B(20,0.15), state mean and variance.", "Mean 3, variance 2.55.", "Use np and np(1-p)."),
            ("Let Y~N(50,8^2). Find P(Y<58).", "About 0.8413.", "Standardize: z=(58-50)/8=1."),
            ("Scores are N(70,6^2). Find the score exceeded by the top 10%.", "About 77.7.", "Use inverse normal with cumulative probability 0.90."),
            ("State two conditions for a binomial model.", "Fixed independent trials, two outcomes, constant p.", "List conditions and relate them to context."),
            ("For X~B(5,0.2), find P(X>=1).", "1-0.8^5.", "Use the complement P(at least one)=1-P(none)."),
            ("A machine fills bottles with N(500,4^2). Find P(496<X<508).", "About 0.8186.", "Standardize to z=-1 and z=2, then subtract cumulative probabilities."),
            ("Use the distribution tool to compare binomial and normal shapes.", "Large n and moderate p make the binomial more bell-shaped.", "Discuss discreteness, centre, spread, and approximation."),
            ("Explain why normal probabilities are areas, not heights.", "The normal variable is continuous.", "For continuous distributions, probability over an interval is area under the density curve."),
        ]
        p, ans, sol = prompts[t]
        return qq("Paper 2", 5 + (t % 4), p, ans, steps(sol, "Use technology values to three significant figures unless exact form is requested."), visual)
    seed = chapter["questions"][k % len(chapter["questions"])]
    return qq(seed.mode, seed.marks, seed.prompt, seed.answer, steps("Identify the relevant method from the chapter.", "Substitute the given values carefully.", "Complete the calculation and state the answer in context."), visual)


def tool_family(chapter: dict) -> str:
    return {
        1: "sequence", 2: "mapping", 3: "quadratic", 4: "rational", 5: "derivative",
        6: "stats", 7: "scatter", 8: "probability", 9: "exponential", 10: "integral",
        11: "geometry3d", 12: "trig", 13: "motion", 14: "distribution",
    }.get(chapter["n"], "curve")


def render_tool(chapter: dict, zone: str, variant: int) -> str:
    family = tool_family(chapter)
    mode = "solid3d" if family == "geometry3d" and variant == 2 else family
    title = {
        "hook": "Live hook manipulative",
        "build1": "Exploration tool A",
        "build2": "Exploration tool B",
    }[zone]
    prompts = {
        "sequence": "Edit first term, change, and zoom to compare term growth and accumulated totals.",
        "mapping": "Edit a function rule and watch domain, range, composition, and inverse behaviour.",
        "quadratic": "Edit the vertex form and inspect intercepts, vertex, and transformations.",
        "rational": "Move asymptotes and inspect reciprocal behaviour near restricted values.",
        "derivative": "Drag the tangent location and compare the curve with its rate of change.",
        "stats": "Move data controls and compare centre, spread, outliers, and representation.",
        "scatter": "Edit scatter strength and slope, then compare regression and residual behaviour.",
        "probability": "Adjust event sizes and inspect Venn, tree, and conditional probability structure.",
        "exponential": "Edit initial value and growth factor, then compare exponential and logarithmic views.",
        "integral": "Change the curve and interval to compare signed area and accumulated area.",
        "geometry3d": "Rotate, zoom, and switch views of a crisp 3D model for spatial reasoning.",
        "trig": "Edit amplitude, period, and phase while linking the unit circle to the wave.",
        "motion": "Edit motion parameters and compare displacement, velocity, and acceleration.",
        "distribution": "Edit mean, spread, sample size, and probability cutoffs on distribution models.",
    }
    return f"""
    <div class="toolcard manip-tool" data-family="{family}" data-mode="{mode}" data-variant="{variant}">
      <div class="toolhead">
        <div><span class="sectlabel">{esc(title)}</span><h3>{esc(chapter['title'].split(':')[0])}</h3></div>
        <div class="toolbuttons">
          <button class="btn ghost mini-btn" type="button" data-act="zoom-in">Zoom +</button>
          <button class="btn ghost mini-btn" type="button" data-act="zoom-out">Zoom -</button>
          <button class="btn ghost mini-btn" type="button" data-act="reset">Reset</button>
          <button class="btn ghost mini-btn view3d" type="button" data-act="view">View</button>
        </div>
      </div>
      <p>{esc(prompts[family])}</p>
      <div class="toolstage">
        <svg class="toolsvg" viewBox="0 0 900 520" role="img" aria-label="Interactive mathematical graph"></svg>
        <canvas class="toolcanvas" width="1200" height="720" aria-label="Rotatable 3D mathematical model"></canvas>
      </div>
      <div class="toolcontrols">
        <label>A <input type="range" min="-5" max="8" step="0.1" value="{1 + variant}" data-param="a"></label>
        <label>B <input type="range" min="-6" max="6" step="0.1" value="{variant - 1}" data-param="b"></label>
        <label>C <input type="range" min="-5" max="8" step="0.1" value="{2 - variant}" data-param="c"></label>
      </div>
      <div class="readout toolreadout">Edit the controls, zoom the graph, or drag inside the stage.</div>
    </div>
    """


def render_rich_learn(chapter: dict) -> str:
    body = []
    body.append(f"""
    <div class="learn-brief card">
      <span class="sectlabel">Cambridge examiner lens</span>
      <p class="lead">This chapter is not only about getting an answer. It is about choosing a representation, showing a valid method, communicating restrictions, and interpreting the result in the language of the situation.</p>
      <p>Students should read every worked example in four passes: what is being modelled, which mathematical object is being used, what calculation is justified, and what the final answer means. That habit is what separates a correct-looking response from a response that earns full method, accuracy, reasoning, and communication marks.</p>
    </div>
    """)
    body.append('<div class="grid2">')
    for title, text in chapter["learn"]:
        body.append(f"""
        <div class="card glow">
          <h3>{esc(title)}</h3>
          <p>{esc(text)}</p>
          <div class="callout key"><span class="lab">Understand</span><p>Connect this idea to a graph, table, equation, and verbal explanation. If one representation changes, explain what changes in the others.</p></div>
        </div>
        """)
    body.append("</div>")
    body.append(f"""
    <div class="grid3 learn-deep">
      <div class="card"><h3>Representation</h3><p>Use the Oxford sequence topics as checkpoints: {esc('; '.join(chapter['toc'][:3]))}. Build fluency by moving between symbolic, graphical, numerical, and contextual forms.</p></div>
      <div class="card"><h3>Reasoning</h3><p>Before calculating, name the theorem, rule, model, or distribution being used. After calculating, check domain, units, reasonableness, and whether technology output needs rounding.</p></div>
      <div class="card"><h3>Common loss of marks</h3><p>Students often lose marks by skipping setup, rounding too early, ignoring restrictions, or giving a number without interpretation. The solution bank models the expected chain of reasoning.</p></div>
    </div>
    """)
    return "\n".join(body)


def render_question_visual(q: Question, i: int) -> str:
    if not q.visual:
        return ""
    return f"""
    <div class="qfigure zoom-figure" data-visual="{esc(q.visual)}" data-seed="{i}">
      <div class="qfigbar">
        <span>Graphical stimulus</span>
        <button type="button" data-qzoom="in">Zoom +</button>
        <button type="button" data-qzoom="out">Zoom -</button>
        <button type="button" data-qzoom="reset">Reset</button>
      </div>
      <svg viewBox="0 0 760 360" role="img" aria-label="Zoomable editable exam graph"></svg>
      <p class="boardhelp">Zoomable graph. Drag inside the graph to move the highlighted point or model parameter.</p>
    </div>
    """


def render_solution(q: Question) -> str:
    raw_steps = [s.strip() for s in (q.solution or "").split("||") if s.strip()]
    if not raw_steps:
        raw_steps = [
            "Identify the relevant chapter method.",
            "Substitute the given values carefully.",
            f"Complete the calculation to obtain {q.answer}",
        ]
    lis = "".join(f"<li>{esc(step)}</li>" for step in raw_steps)
    return f"""
    <div class="solutionbox hidden">
      <span class="lab">Full worked solution</span>
      <ol>{lis}</ol>
      <div class="answerline"><span class="lab">Final answer</span>{esc(q.answer)}</div>
    </div>
    """


def render_questions(items: list[Question]) -> str:
    nav = "".join(
        f"<button type=\"button\" data-go=\"{i-1}\" class=\"navcell{' current' if i == 1 else ''}\">{i}</button>"
        for i in range(1, len(items) + 1)
    )
    cards = []
    for i, q in enumerate(items, 1):
        cards.append(
            f"""
            <article class="qcard exam-card{' active' if i == 1 else ''}" data-q="{i-1}">
              <div class="qhead">
                <span class="qtype">{esc(q.mode)}</span>
                <span class="pracmeta"><b>Question {i} of {len(items)}</b> &middot; [{q.marks} marks]</span>
              </div>
              {render_question_visual(q, i)}
              <p>{esc(q.prompt)}</p>
              <div class="exam-actions">
                <button class="btn ghost solution-toggle" type="button">Show solution</button>
              </div>
              {render_solution(q)}
            </article>
            """
        )
    return f"""
    <div class="exam-shell" data-exam>
      <div class="practop">
        <div class="timer calm">Exam mode</div>
        <div class="pracmeta"><b>{len(items)}</b> questions &middot; one question visible at a time &middot; full solutions hidden</div>
      </div>
      <div class="navpalette exam-nav" aria-label="Question navigation">{nav}</div>
      <div class="exam-stage">{"".join(cards)}</div>
      <div class="exam-footer">
        <button class="btn ghost exam-prev" type="button">Previous</button>
        <div class="readout exam-readout">Question 1 selected.</div>
        <button class="btn primary exam-next" type="button">Next</button>
      </div>
    </div>
    """


EXTRA_CSS = """
.card.slim{padding:14px 16px}
.card.slim p{margin:.2em 0;color:var(--ink)}
.sourcechips{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.sourcechip{display:inline-flex;gap:7px;align-items:center;border:1px solid var(--line);background:rgba(255,255,255,.04);border-radius:999px;padding:7px 10px;font-size:12px;color:var(--ink-soft)}
.sourcechip b{font-family:var(--f-mono);font-size:10px;color:var(--cyan-2);text-transform:uppercase;letter-spacing:.09em}
.exam-card{margin:14px 0}
.exam-card .answerline{display:block;margin-top:12px}
.exam-card .answerline.hidden{display:none}
.statusbar{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px;margin:16px 0}
.statuspill{border:1px solid var(--line);background:var(--surface);border-radius:13px;padding:12px 14px}
.statuspill span{display:block;font-family:var(--f-mono);font-size:10.5px;text-transform:uppercase;letter-spacing:.14em;color:var(--muted)}
.statuspill b{display:block;color:#fff;margin-top:3px}
.mini{border-left:3px solid var(--gold);background:rgba(244,185,23,.08)}
.indexgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(255px,1fr));gap:14px;margin-top:18px}
.indexcard{text-decoration:none;display:block}
.indexcard h3{margin:.15em 0 .2em}
.indexcard:hover{border-color:var(--line-cyan);transform:translateY(-2px)}
.footer-note{font-family:var(--f-mono);font-size:11px;color:var(--muted);margin-top:18px}
.learn-brief{margin-bottom:18px;border-left:3px solid var(--cyan)}
.learn-deep{margin-top:18px}
.toolcard{background:linear-gradient(180deg,rgba(11,24,92,.92),rgba(5,13,52,.96));border:1px solid var(--line);border-radius:16px;padding:16px;margin:16px 0;box-shadow:0 18px 46px rgba(0,0,0,.28)}
.toolhead{display:flex;justify-content:space-between;gap:14px;align-items:flex-start}
.toolhead h3{margin:.1em 0 .2em}
.toolbuttons{display:flex;flex-wrap:wrap;gap:7px;justify-content:flex-end}
.mini-btn{padding:7px 10px;font-size:12px;border-radius:9px}
.toolstage{position:relative;border:1px solid rgba(0,255,250,.22);border-radius:14px;overflow:hidden;background:radial-gradient(circle at 50% 35%,rgba(0,255,250,.08),rgba(0,6,31,.96));min-height:360px}
.toolsvg{display:block;width:100%;height:min(54vw,520px);min-height:360px;touch-action:none}
.toolcanvas{display:none;width:100%;height:min(54vw,520px);min-height:360px;touch-action:none}
.manip-tool[data-mode="solid3d"] .toolsvg{display:none}
.manip-tool[data-mode="solid3d"] .toolcanvas{display:block}
.toolcontrols{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-top:12px}
.toolcontrols label{display:grid;gap:5px;font-family:var(--f-mono);font-size:11px;color:var(--muted);letter-spacing:.08em;text-transform:uppercase}
.toolcontrols input{width:100%;accent-color:var(--cyan)}
.toolreadout{font-size:12px}
.exam-shell{margin-top:14px}
.exam-stage{min-height:540px}
.exam-card{display:none;margin:14px 0}
.exam-card.active{display:block}
.exam-card>p{font-size:18px;line-height:1.7;color:var(--ink)}
.exam-actions{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}
.exam-footer{display:grid;grid-template-columns:auto 1fr auto;gap:10px;align-items:center;margin-top:12px}
.solutionbox{border:1px solid rgba(52,227,160,.32);border-left:4px solid var(--good);background:rgba(52,227,160,.08);border-radius:13px;padding:14px 16px;margin-top:14px}
.solutionbox.hidden{display:none}
.solutionbox .lab{font-family:var(--f-mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--good)}
.solutionbox ol{margin:10px 0 0 22px;color:var(--ink-soft);line-height:1.7}
.solutionbox li{margin:7px 0}
.qfigure{border:1px solid var(--line);background:rgba(1,8,46,.9);border-radius:13px;padding:10px;margin:12px 0}
.qfigure svg{display:block;width:100%;height:320px;touch-action:none}
.qfigbar{display:flex;gap:8px;justify-content:space-between;align-items:center;margin-bottom:8px;font-family:var(--f-mono);font-size:11px;color:var(--cyan-2);text-transform:uppercase;letter-spacing:.1em}
.qfigbar button{border:1px solid var(--line);background:rgba(255,255,255,.04);color:var(--ink);border-radius:8px;padding:5px 8px;cursor:pointer}
.exam-nav{grid-template-columns:repeat(auto-fill,minmax(38px,1fr));max-height:194px}
.exam-nav .navcell.current{outline:2px solid var(--cyan);color:#fff}
.exam-nav .navcell.seen{background:rgba(52,227,160,.12);border-color:rgba(52,227,160,.34)}
@media(max-width:720px){.toolhead,.exam-footer{grid-template-columns:1fr;display:grid}.toolbuttons{justify-content:flex-start}.exam-stage{min-height:460px}.qfigure svg{height:260px}}
"""


COMMON_JS = """
document.addEventListener('DOMContentLoaded', function(){
  document.querySelectorAll('.tabbtn').forEach(function(btn){
    btn.addEventListener('click', function(){
      var id = btn.getAttribute('data-tab');
      document.querySelectorAll('.tabbtn').forEach(function(b){ b.classList.remove('on'); });
      document.querySelectorAll('.panel-tab').forEach(function(p){ p.classList.remove('on'); });
      btn.classList.add('on');
      var panel = document.getElementById('panel-' + id);
      if(panel) panel.classList.add('on');
    });
  });
  document.querySelectorAll('.reveal').forEach(function(btn){
    btn.addEventListener('click', function(){
      var ans = btn.parentElement.querySelector('.answerline');
      if(!ans) return;
      ans.classList.toggle('hidden');
      btn.textContent = ans.classList.contains('hidden') ? 'Show answer' : 'Hide answer';
    });
  });
  if(window.renderMathInElement){
    renderMathInElement(document.body, {
      delimiters: [
        {left: '$$', right: '$$', display: true},
        {left: '$', right: '$', display: false}
      ],
      throwOnError: false
    });
  }
});
"""


COMMON_JS = """
document.addEventListener('DOMContentLoaded', function(){
  function qs(root, sel){ return root.querySelector(sel); }
  function qsa(root, sel){ return Array.prototype.slice.call(root.querySelectorAll(sel)); }

  qsa(document, '.tabbtn').forEach(function(btn){
    btn.addEventListener('click', function(){
      var id = btn.getAttribute('data-tab');
      qsa(document, '.tabbtn').forEach(function(b){ b.classList.remove('on'); });
      qsa(document, '.panel-tab').forEach(function(p){ p.classList.remove('on'); });
      btn.classList.add('on');
      var panel = document.getElementById('panel-' + id);
      if(panel) panel.classList.add('on');
    });
  });

  function initExam(exam){
    var cards = qsa(exam, '.exam-card');
    var nav = qsa(exam, '.exam-nav .navcell');
    var readout = qs(exam, '.exam-readout');
    var current = 0;
    function show(i){
      current = Math.max(0, Math.min(cards.length - 1, i));
      cards.forEach(function(card, idx){ card.classList.toggle('active', idx === current); });
      nav.forEach(function(btn, idx){
        btn.classList.toggle('current', idx === current);
        if(idx <= current) btn.classList.add('seen');
      });
      if(readout) readout.textContent = 'Question ' + (current + 1) + ' selected.';
    }
    nav.forEach(function(btn){
      btn.addEventListener('click', function(){ show(parseInt(btn.getAttribute('data-go'), 10)); });
    });
    var prev = qs(exam, '.exam-prev');
    var next = qs(exam, '.exam-next');
    if(prev) prev.addEventListener('click', function(){ show(current - 1); });
    if(next) next.addEventListener('click', function(){ show(current + 1); });
    qsa(exam, '.solution-toggle').forEach(function(btn){
      btn.addEventListener('click', function(){
        var card = btn.closest('.exam-card');
        var box = qs(card, '.solutionbox');
        if(!box) return;
        box.classList.toggle('hidden');
        btn.textContent = box.classList.contains('hidden') ? 'Show solution' : 'Hide solution';
      });
    });
    show(0);
  }

  function svgMarkupForVisual(kind, seed, zoom, shift){
    var W = 760, H = 360, midY = 180, midX = 380;
    var minX = -10 / zoom + shift, maxX = 10 / zoom + shift;
    function X(x){ return (x - minX) / (maxX - minX) * W; }
    function Y(y){ return midY - y * 24 * zoom; }
    function pathFor(fn){
      var d = '';
      for(var i=0;i<=220;i++){
        var x = minX + (maxX-minX)*i/220;
        var y = fn(x);
        if(!isFinite(y) || Math.abs(y)>80){ d += ''; continue; }
        d += (d ? ' L ' : 'M ') + X(x).toFixed(1) + ' ' + Y(y).toFixed(1);
      }
      return d;
    }
    var grid = '<rect width="760" height="360" fill="#020a26"/>';
    for(var gx=-10; gx<=10; gx++){ grid += '<line x1="'+X(gx)+'" y1="0" x2="'+X(gx)+'" y2="360" stroke="rgba(120,150,255,.13)"/>'; }
    for(var gy=-6; gy<=6; gy++){ grid += '<line x1="0" y1="'+Y(gy)+'" x2="760" y2="'+Y(gy)+'" stroke="rgba(120,150,255,.13)"/>'; }
    grid += '<line x1="0" y1="'+Y(0)+'" x2="760" y2="'+Y(0)+'" stroke="#5e6fa6"/><line x1="'+X(0)+'" y1="0" x2="'+X(0)+'" y2="360" stroke="#5e6fa6"/>';
    var a = 1 + (seed % 5) * .35, b = (seed % 7) - 3, c = ((seed * 3) % 9) - 4;
    var body = '';
    if(kind === 'stats'){
      for(var j=0;j<9;j++){ var h=40+((j*seed)%9)*22; body += '<rect x="'+(70+j*68)+'" y="'+(310-h)+'" width="44" height="'+h+'" fill="rgba(0,255,250,.35)" stroke="#00fffa"/>'; }
    } else if(kind === 'scatter'){
      body += '<path d="'+pathFor(function(x){return .55*x+1;})+'" fill="none" stroke="#f5e60d" stroke-width="3"/>';
      for(var s=0;s<18;s++){ var px=-8+s; var py=.55*px+1+Math.sin(s+seed)*1.4; body += '<circle cx="'+X(px)+'" cy="'+Y(py)+'" r="5" fill="#e045ff"/>'; }
    } else if(kind === 'probability'){
      body += '<circle cx="320" cy="180" r="96" fill="rgba(0,255,250,.22)" stroke="#00fffa" stroke-width="3"/><circle cx="440" cy="180" r="96" fill="rgba(224,69,255,.20)" stroke="#e045ff" stroke-width="3"/><text x="275" y="180" fill="#eaf1ff" font-size="24">A</text><text x="475" y="180" fill="#eaf1ff" font-size="24">B</text><text x="374" y="185" fill="#f5e60d" font-size="18">A and B</text>';
    } else if(kind === 'geometry'){
      body += '<polygon points="160,290 620,290 500,80" fill="rgba(0,255,250,.10)" stroke="#00fffa" stroke-width="3"/><line x1="500" y1="80" x2="500" y2="290" stroke="#f5e60d" stroke-width="3" stroke-dasharray="8 6"/><text x="510" y="190" fill="#f5e60d" font-size="18">height</text>';
    } else if(kind === 'trig'){
      body += '<path d="'+pathFor(function(x){return 2*Math.sin(a*x+b)+c/3;})+'" fill="none" stroke="#00fffa" stroke-width="4"/><circle cx="'+X(0)+'" cy="'+Y(0)+'" r="70" fill="none" stroke="#f5e60d" stroke-width="2"/>';
    } else if(kind === 'distribution'){
      body += '<path d="'+pathFor(function(x){return 5*Math.exp(-0.5*Math.pow((x-b)/2,2));})+'" fill="none" stroke="#00fffa" stroke-width="4"/><path d="'+pathFor(function(x){return 5*Math.exp(-0.5*Math.pow((x-b)/2,2));})+' L '+X(maxX)+' '+Y(0)+' L '+X(minX)+' '+Y(0)+' Z" fill="rgba(0,255,250,.12)"/>';
    } else if(kind === 'rational'){
      body += '<path d="'+pathFor(function(x){return a/(x-b)+c/3;})+'" fill="none" stroke="#00fffa" stroke-width="4"/><line x1="'+X(b)+'" y1="0" x2="'+X(b)+'" y2="360" stroke="#f5e60d" stroke-dasharray="7 7"/>';
    } else if(kind === 'integral'){
      var d = pathFor(function(x){return .12*x*x-1;});
      body += '<path d="'+d+' L '+X(maxX)+' '+Y(0)+' L '+X(minX)+' '+Y(0)+' Z" fill="rgba(0,255,250,.16)"/><path d="'+d+'" fill="none" stroke="#00fffa" stroke-width="4"/>';
    } else if(kind === 'derivative' || kind === 'motion'){
      body += '<path d="'+pathFor(function(x){return .04*x*x*x-.4*x+c/3;})+'" fill="none" stroke="#00fffa" stroke-width="4"/><path d="'+pathFor(function(x){return .12*x*x-.4;})+'" fill="none" stroke="#f5e60d" stroke-width="3" stroke-dasharray="8 6"/>';
    } else if(kind === 'exponential'){
      body += '<path d="'+pathFor(function(x){return Math.exp(.25*x)-2;})+'" fill="none" stroke="#00fffa" stroke-width="4"/><path d="'+pathFor(function(x){return Math.log(Math.max(.05,x+7))-2;})+'" fill="none" stroke="#f5e60d" stroke-width="3"/>';
    } else {
      body += '<path d="'+pathFor(function(x){return a*(x-b)*(x-b)/6+c/3;})+'" fill="none" stroke="#00fffa" stroke-width="4"/>';
    }
    return grid + body;
  }

  function initQuestionFigure(fig){
    var svg = qs(fig, 'svg');
    var zoom = 1, shift = 0;
    var kind = fig.getAttribute('data-visual') || 'curve';
    var seed = parseInt(fig.getAttribute('data-seed') || '1', 10);
    function draw(){ svg.innerHTML = svgMarkupForVisual(kind, seed, zoom, shift); }
    qsa(fig, '[data-qzoom]').forEach(function(btn){
      btn.addEventListener('click', function(){
        var act = btn.getAttribute('data-qzoom');
        if(act === 'in') zoom *= 1.25;
        if(act === 'out') zoom /= 1.25;
        if(act === 'reset'){ zoom = 1; shift = 0; }
        draw();
      });
    });
    svg.addEventListener('pointerdown', function(ev){ shift += (ev.offsetX - 380) / 120; draw(); });
    draw();
  }

  function initTool(tool){
    var svg = qs(tool, '.toolsvg');
    var canvas = qs(tool, '.toolcanvas');
    var readout = qs(tool, '.toolreadout');
    var family = tool.getAttribute('data-family') || 'curve';
    var mode = tool.getAttribute('data-mode') || family;
    var state = { a: 2, b: 0, c: 1, zoom: 1, rotX: -.55, rotY: .72, dragging: false, lx: 0, ly: 0 };
    qsa(tool, 'input[data-param]').forEach(function(inp){
      state[inp.getAttribute('data-param')] = parseFloat(inp.value);
      inp.addEventListener('input', function(){ state[inp.getAttribute('data-param')] = parseFloat(inp.value); draw(); });
    });
    qsa(tool, '[data-act]').forEach(function(btn){
      btn.addEventListener('click', function(){
        var act = btn.getAttribute('data-act');
        if(act === 'zoom-in') state.zoom *= 1.2;
        if(act === 'zoom-out') state.zoom /= 1.2;
        if(act === 'reset'){ state.zoom = 1; state.rotX = -.55; state.rotY = .72; }
        if(act === 'view'){ state.rotX += .55; state.rotY += .7; }
        draw();
      });
    });
    function mapX(x){ return 450 + x * 38 * state.zoom; }
    function mapY(y){ return 260 - y * 38 * state.zoom; }
    function path(fn){
      var d = '';
      for(var i=0;i<=300;i++){
        var x = -10/state.zoom + 20/state.zoom*i/300;
        var y = fn(x);
        if(!isFinite(y) || Math.abs(y)>50) continue;
        d += (d ? ' L ' : 'M ') + mapX(x).toFixed(1) + ' ' + mapY(y).toFixed(1);
      }
      return d;
    }
    function drawSvg(){
      var a = state.a || 1, b = state.b || 0, c = state.c || 0;
      var s = '<rect width="900" height="520" fill="#020a26"/>';
      for(var x=-12;x<=12;x++){ s += '<line x1="'+mapX(x)+'" y1="0" x2="'+mapX(x)+'" y2="520" stroke="rgba(120,150,255,.12)"/>'; }
      for(var y=-7;y<=7;y++){ s += '<line x1="0" y1="'+mapY(y)+'" x2="900" y2="'+mapY(y)+'" stroke="rgba(120,150,255,.12)"/>'; }
      s += '<line x1="0" y1="'+mapY(0)+'" x2="900" y2="'+mapY(0)+'" stroke="#5e6fa6"/><line x1="'+mapX(0)+'" y1="0" x2="'+mapX(0)+'" y2="520" stroke="#5e6fa6"/>';
      if(family === 'sequence'){
        for(var n=1;n<=14;n++){ var y=a+(n-1)*b; s += '<circle cx="'+mapX(n-7)+'" cy="'+mapY(y/3)+'" r="7" fill="#00fffa"/><line x1="'+mapX(n-7)+'" y1="'+mapY(0)+'" x2="'+mapX(n-7)+'" y2="'+mapY(y/3)+'" stroke="rgba(0,255,250,.45)"/>'; }
      } else if(family === 'stats'){
        for(var j=0;j<10;j++){ var h=50+Math.abs(Math.sin(j+a))*150+20*b; s += '<rect x="'+(95+j*70)+'" y="'+(440-h)+'" width="46" height="'+h+'" fill="rgba(0,255,250,.32)" stroke="#00fffa"/>'; }
      } else if(family === 'scatter'){
        s += '<path d="'+path(function(x){return .55*a*x+c;})+'" fill="none" stroke="#f5e60d" stroke-width="4"/>';
        for(var p=0;p<24;p++){ var px=-9+p*.8; var py=.55*a*px+c+Math.sin(p+b)*1.3; s += '<circle cx="'+mapX(px)+'" cy="'+mapY(py)+'" r="6" fill="#e045ff"/>'; }
      } else if(family === 'probability'){
        s += '<circle cx="380" cy="255" r="'+(100+8*a)+'" fill="rgba(0,255,250,.22)" stroke="#00fffa" stroke-width="4"/><circle cx="520" cy="255" r="'+(100+8*b)+'" fill="rgba(224,69,255,.18)" stroke="#e045ff" stroke-width="4"/><text x="327" y="260" fill="#eaf1ff" font-size="28">A</text><text x="555" y="260" fill="#eaf1ff" font-size="28">B</text><text x="426" y="262" fill="#f5e60d" font-size="18">intersection</text>';
      } else if(family === 'trig'){
        s += '<circle cx="190" cy="250" r="92" fill="none" stroke="#f5e60d" stroke-width="3"/><path d="'+path(function(x){return a*Math.sin((b+2)*x/3)+c;})+'" fill="none" stroke="#00fffa" stroke-width="4"/>';
      } else if(family === 'distribution'){
        s += '<path d="'+path(function(x){return 5*Math.exp(-.5*Math.pow((x-b)/(Math.abs(a)+1),2));})+'" fill="none" stroke="#00fffa" stroke-width="4"/>';
        for(var k=0;k<12;k++){ var bx=-5+k*.8; var bh=120*Math.exp(-.5*Math.pow((bx-b)/(Math.abs(a)+1),2)); s += '<rect x="'+mapX(bx)+'" y="'+(mapY(0)-bh)+'" width="18" height="'+bh+'" fill="rgba(245,230,13,.32)" stroke="#f5e60d"/>'; }
      } else if(family === 'rational'){
        s += '<line x1="'+mapX(b)+'" y1="0" x2="'+mapX(b)+'" y2="520" stroke="#f5e60d" stroke-dasharray="9 7"/><line x1="0" y1="'+mapY(c)+'" x2="900" y2="'+mapY(c)+'" stroke="#f5e60d" stroke-dasharray="9 7"/><path d="'+path(function(x){return a/(x-b)+c;})+'" fill="none" stroke="#00fffa" stroke-width="4"/>';
      } else if(family === 'integral'){
        var d = path(function(x){return .08*a*x*x+b*x/4+c;});
        s += '<path d="'+d+' L '+mapX(10/state.zoom)+' '+mapY(0)+' L '+mapX(-10/state.zoom)+' '+mapY(0)+' Z" fill="rgba(0,255,250,.15)"/><path d="'+d+'" fill="none" stroke="#00fffa" stroke-width="4"/>';
      } else if(family === 'derivative' || family === 'motion'){
        s += '<path d="'+path(function(x){return .05*x*x*x-b*x+c;})+'" fill="none" stroke="#00fffa" stroke-width="4"/><path d="'+path(function(x){return .15*x*x-b;})+'" fill="none" stroke="#f5e60d" stroke-width="3" stroke-dasharray="8 7"/>';
      } else if(family === 'exponential'){
        s += '<path d="'+path(function(x){return a*Math.exp(.18*(x-b))+c-3;})+'" fill="none" stroke="#00fffa" stroke-width="4"/><path d="'+path(function(x){return Math.log(Math.max(.05,x+8))-2+c/4;})+'" fill="none" stroke="#f5e60d" stroke-width="3"/>';
      } else if(family === 'geometry3d'){
        s += '<polygon points="180,420 700,420 560,90" fill="rgba(0,255,250,.08)" stroke="#00fffa" stroke-width="4"/><line x1="560" y1="90" x2="560" y2="420" stroke="#f5e60d" stroke-width="4" stroke-dasharray="9 7"/>';
      } else {
        s += '<path d="'+path(function(x){return a*(x-b)*(x-b)/5+c;})+'" fill="none" stroke="#00fffa" stroke-width="4"/>';
      }
      svg.innerHTML = s;
      if(readout) readout.textContent = 'A=' + a.toFixed(2) + ', B=' + b.toFixed(2) + ', C=' + c.toFixed(2) + ', zoom=' + state.zoom.toFixed(2);
    }
    function draw3d(){
      var ctx = canvas.getContext('2d');
      var w = canvas.width, h = canvas.height;
      ctx.clearRect(0,0,w,h);
      var grad = ctx.createRadialGradient(w/2,h/2,20,w/2,h/2,w/1.2);
      grad.addColorStop(0,'#071a55'); grad.addColorStop(1,'#00061f');
      ctx.fillStyle = grad; ctx.fillRect(0,0,w,h);
      var pts = [[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1],[0,0,1.8]];
      function project(p){
        var x=p[0], y=p[1], z=p[2];
        var cy=Math.cos(state.rotY), sy=Math.sin(state.rotY), cx=Math.cos(state.rotX), sx=Math.sin(state.rotX);
        var x1=x*cy-z*sy, z1=x*sy+z*cy, y1=y*cx-z1*sx, z2=y*sx+z1*cx;
        var sc=210*state.zoom/(3.5+z2);
        return [w/2+x1*sc, h/2-y1*sc];
      }
      var edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7],[4,8],[5,8],[6,8],[7,8]];
      ctx.lineWidth = 4; ctx.strokeStyle = '#00fffa'; ctx.shadowColor = '#00fffa'; ctx.shadowBlur = 12;
      edges.forEach(function(e){ var a=project(pts[e[0]]), b=project(pts[e[1]]); ctx.beginPath(); ctx.moveTo(a[0],a[1]); ctx.lineTo(b[0],b[1]); ctx.stroke(); });
      ctx.shadowBlur = 0; ctx.fillStyle = '#f5e60d'; ctx.font = '24px sans-serif'; ctx.fillText('Drag to rotate - wheel/buttons to zoom', 34, 46);
      if(readout) readout.textContent = '3D viewer: rotatable, zoomable, and view-switchable.';
    }
    function draw(){ mode === 'solid3d' ? draw3d() : drawSvg(); }
    var stage = mode === 'solid3d' ? canvas : svg;
    stage.addEventListener('wheel', function(ev){ ev.preventDefault(); state.zoom *= ev.deltaY < 0 ? 1.08 : .92; draw(); }, { passive:false });
    stage.addEventListener('pointerdown', function(ev){ state.dragging = true; state.lx = ev.clientX; state.ly = ev.clientY; stage.setPointerCapture && stage.setPointerCapture(ev.pointerId); });
    stage.addEventListener('pointermove', function(ev){
      if(!state.dragging) return;
      var dx = ev.clientX - state.lx, dy = ev.clientY - state.ly;
      state.lx = ev.clientX; state.ly = ev.clientY;
      if(mode === 'solid3d'){ state.rotY += dx*.01; state.rotX += dy*.01; }
      else { state.b += dx*.01; state.c -= dy*.01; }
      draw();
    });
    stage.addEventListener('pointerup', function(){ state.dragging = false; });
    draw();
  }

  qsa(document, '[data-exam]').forEach(initExam);
  qsa(document, '.zoom-figure').forEach(initQuestionFigure);
  qsa(document, '.manip-tool').forEach(initTool);

  if(window.renderMathInElement){
    renderMathInElement(document.body, {
      delimiters: [
        {left: '$$', right: '$$', display: true},
        {left: '$', right: '$', display: false}
      ],
      throwOnError: false
    });
  }
});
"""


def chapter_html(chapter: dict, tpl: dict[str, str]) -> str:
    title = chapter["title"]
    filename = slug(chapter["n"], title)
    questions = make_exam_questions(chapter)
    prev_link = "" if chapter["n"] == 1 else f"<a class=\"btn ghost\" href=\"{slug(chapter['n']-1, CHAPTERS[chapter['n']-2]['title'])}\">Previous</a>"
    next_link = "" if chapter["n"] == len(CHAPTERS) else f"<a class=\"btn ghost\" href=\"{slug(chapter['n']+1, CHAPTERS[chapter['n']]['title'])}\">Next</a>"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Spi-Math AASL | Chapter {chapter['n']:02d}</title>
{tpl['head_links']}
<style>
{tpl['base_style']}
{EXTRA_CSS}
</style>
</head>
<body>
{tpl['header']}
<main class="wrap" id="top">
  <section class="hero">
    <p class="kicker">spi-math-ibdp-aasl · Chapter {chapter['n']:02d}</p>
    <h1>{esc(title)}<em>{esc(chapter['subtitle'])}</em></h1>
    <p class="lead">This enhanced AASL document follows the locked Spi-Math single-page structure while adding examiner-level explanations, topic manipulatives, graphical analysis, and an 80-question exam-mode practice bank.</p>
    <div class="meta"><span><b>Status</b> enhanced AASL build</span><span><b>Originals</b> untouched</span><span><b>Question bank</b> {len(questions)} IB-style items</span></div>
  </section>

  <nav class="tabstrip" id="tabstrip" aria-label="Chapter sections">
    <button class="tabbtn on" data-tab="hook"><span class="dot"></span><span class="tnum">01</span> HOOK</button>
    <button class="tabbtn" data-tab="learn"><span class="dot"></span><span class="tnum">02</span> LEARN</button>
    <button class="tabbtn" data-tab="build"><span class="dot"></span><span class="tnum">03</span> BUILD &amp; EXPLORE</button>
    <button class="tabbtn" data-tab="examples"><span class="dot"></span><span class="tnum">04</span> SOLVED EXAMPLES</button>
    <button class="tabbtn" data-tab="practice"><span class="dot"></span><span class="tnum">05</span> PRACTICE</button>
    <button class="tabbtn" data-tab="summary"><span class="dot"></span><span class="tnum">06</span> SUMMARY &amp; NOTES</button>
  </nav>

  <section class="panel-tab on" id="panel-hook">
    <div class="sectlabel">Hook</div>
    <h2 class="big">What this chapter is really about</h2>
    <div class="grid2">
      <div class="card">
        <p class="lead">{esc(chapter['subtitle'])}</p>
        <div class="callout key"><span class="lab">AASL lens</span><p>Every idea is treated as a model: define the variables, choose a representation, calculate with care, then interpret the result in context.</p></div>
      </div>
      <div class="card mini">
        <span class="sectlabel">Oxford sequence</span>
        {render_list(chapter['toc'])}
      </div>
    </div>
    {render_tool(chapter, "hook", 0)}
  </section>

  <section class="panel-tab" id="panel-learn">
    <div class="sectlabel">Learn</div>
    <h2 class="big">Core ideas and syllabus moves</h2>
    {render_rich_learn(chapter)}
  </section>

  <section class="panel-tab" id="panel-build">
    <div class="sectlabel">Build & Explore</div>
    <h2 class="big">Classroom build path</h2>
    <div class="grid3">
      <div class="card glow"><h3>Technology</h3><p>Use graphing, spreadsheet, or GDC workflows to test parameters, visualize behaviour, and check numerical answers.</p></div>
      <div class="card glow"><h3>Modelling</h3><p>Move from context to variables, assumptions, equations, computation, and interpretation. Record limitations explicitly.</p></div>
      <div class="card glow"><h3>Exam move</h3><p>Write enough method for IB marks: formula, substitution, calculation, and contextual conclusion with units where relevant.</p></div>
    </div>
    <div class="grid2">
      {render_tool(chapter, "build1", 1)}
      {render_tool(chapter, "build2", 2)}
    </div>
    <h3>Chapter coverage</h3>
    {render_toc(chapter['toc'])}
  </section>

  <section class="panel-tab" id="panel-examples">
    <div class="sectlabel">Solved Examples</div>
    <h2 class="big">Worked AASL patterns</h2>
    {render_worked(chapter['worked'])}
  </section>

  <section class="panel-tab" id="panel-practice">
    <div class="sectlabel">Practice</div>
    <h2 class="big">IBDP AASL examination-style questions</h2>
    <p class="lead">Questions are original and written to mirror IB command style, marks, multi-step reasoning, calculator awareness, graphical analysis, and contextual interpretation. Each question appears alone in exam mode; full worked solutions remain hidden until requested.</p>
    {render_questions(questions)}
  </section>

  <section class="panel-tab" id="panel-summary">
    <div class="sectlabel">Summary & Notes</div>
    <h2 class="big">Teacher notes and source map</h2>
    <div class="statusbar">
      <div class="statuspill"><span>Chapter</span><b>{chapter['n']:02d}</b></div>
      <div class="statuspill"><span>Questions</span><b>{len(questions)} exam-mode items</b></div>
      <div class="statuspill"><span>Identity</span><b>Locked Spi-Math header/footer</b></div>
      <div class="statuspill"><span>Original files</span><b>Read only / untouched</b></div>
    </div>
    <h3>Syllabus connections</h3>
    {render_list(chapter['syllabus'], "sumlist")}
    <h3>Sources collected for this chapter</h3>
    <div class="sourcechips">{render_sources(chapter)}</div>
    <p class="footer-note">Note: no separate official IBO syllabus PDF was found in the folder during inventory. The scope here is anchored to the Oxford AASL ToC, Oxford teacher-note syllabus connections, AASL worksheets/tests, and AA SL specimen-paper style.</p>
    <p style="margin-top:18px"><a class="btn ghost" href="index.html">Index</a> {prev_link} {next_link}</p>
  </section>
</main>
{tpl['footer']}
<script>{COMMON_JS}</script>
</body>
</html>
"""


def build_index(tpl: dict[str, str]) -> str:
    cards = []
    for ch in CHAPTERS:
        file = slug(ch["n"], ch["title"])
        cards.append(
            f"""
            <a class="card glow indexcard" href="{file}">
              <span class="sectlabel">Chapter {ch['n']:02d}</span>
              <h3>{esc(ch['title'])}</h3>
              <p>{esc(ch['subtitle'])}</p>
            </a>
            """
        )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Spi-Math AASL | Curriculum Index</title>
{tpl['head_links']}
<style>
{tpl['base_style']}
{EXTRA_CSS}
</style>
</head>
<body>
{tpl['header']}
<main class="wrap" id="top">
  <section class="hero">
    <p class="kicker">spi-math-ibdp-aasl</p>
    <h1>IBDP Mathematics: Analysis and Approaches SL<em>Full Spi-Math curriculum draft</em></h1>
    <p class="lead">A new set of self-contained Spi-Math HTML documents generated from the high-school technology baseline and aligned to the Oxford AASL chapter sequence.</p>
    <div class="meta"><span><b>Chapters</b> 14</span><span><b>Generated questions</b> {QUESTIONS_PER_CHAPTER * len(CHAPTERS)}</span><span><b>Originals</b> untouched</span></div>
  </section>
  <section>
    <div class="sectlabel">Documents</div>
    <h2 class="big">Chapter documents</h2>
    <div class="indexgrid">{''.join(cards)}</div>
  </section>
</main>
{tpl['footer']}
</body>
</html>
"""


def build_markdown_map() -> str:
    lines = [
        "# spi-math-ibdp-aasl curriculum map",
        "",
        "Original files were inventoried only. New generated documents are in `documents/`.",
        "",
        "## Important source note",
        "",
        "No separate official IBO syllabus PDF was found in `New curricula` during inventory. Scope has been anchored to the Oxford AASL ToC image PDF, the Oxford teacher-note syllabus connections, chapter tests, worksheets, and AA SL specimen-paper style.",
        "",
        "## Chapter map",
        "",
    ]
    for ch in CHAPTERS:
        lines.extend([
            f"### {ch['n']:02d}. {ch['title']}",
            "",
            f"- Output: `documents/{slug(ch['n'], ch['title'])}`",
            f"- Oxford ToC topics: {', '.join(ch['toc'])}",
            f"- High-school source HTML: {', '.join(ch['source_html'])}",
            f"- AASL question count: {QUESTIONS_PER_CHAPTER}",
            "",
        ])
    return "\n".join(lines)


def build_readme() -> str:
    return """# spi-math-ibdp-aasl

This folder contains new Spi-Math IBDP Mathematics: Analysis and Approaches SL curriculum documents.

Non-negotiable source handling:

- The original ZIP and PDFs in `New curricula` were not edited.
- Generated HTML files are written only under `spi-math-ibdp-aasl/documents`.
- QA images extracted from the Oxford ToC PDF are copies under `_qa/toc_pages`.

Current build:

- 14 chapter HTML documents plus an index page.
- Locked Spi-Math header, logo, tagline, footer, and legal identity copied from the high-school HTML template.
- 1120 original IBDP AASL examination-style questions across the chapter set.
- Curriculum map and source inventory generated for traceability.
"""


def build_inventory() -> dict:
    pdfs = sorted(str(p.relative_to(ROOT)) for p in ROOT.glob("**/*.pdf") if PROJECT not in p.parents)
    with ZipFile(ZIP_PATH) as zf:
        zip_entries = [i.filename for i in zf.infolist() if i.filename.endswith(".html")]
    return {
        "project": "spi-math-ibdp-aasl",
        "source_policy": "Original files inventoried/read only; generated files are under spi-math-ibdp-aasl.",
        "official_ibo_syllabus_pdf_found": False,
        "counts": {
            "source_pdfs": len(pdfs),
            "source_high_school_html_in_zip": len(zip_entries),
            "generated_chapters": len(CHAPTERS),
            "generated_questions": QUESTIONS_PER_CHAPTER * len(CHAPTERS),
        },
        "source_pdfs": pdfs,
        "high_school_zip_html": zip_entries,
        "generated_documents": [f"documents/{slug(ch['n'], ch['title'])}" for ch in CHAPTERS],
    }


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    tpl = extract_template_parts()
    (DOCS / "index.html").write_text(build_index(tpl), encoding="utf-8")
    for chapter in CHAPTERS:
        (DOCS / slug(chapter["n"], chapter["title"])).write_text(chapter_html(chapter, tpl), encoding="utf-8")
    (PROJECT / "README.md").write_text(build_readme(), encoding="utf-8")
    (PROJECT / "curriculum-map.md").write_text(build_markdown_map(), encoding="utf-8")
    (PROJECT / "source-inventory.json").write_text(json.dumps(build_inventory(), indent=2), encoding="utf-8")
    print(f"Generated {len(CHAPTERS)} chapters and index in {DOCS}")


if __name__ == "__main__":
    main()
