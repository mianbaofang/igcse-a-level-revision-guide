from __future__ import annotations

from intl_exam_guide.planning.subject_profiles import has_terms


def mathematics_specialist_example(
    text: str,
    number: int,
) -> tuple[str, list[str], list[str], list[str]]:
    if has_terms(text, ["relative frequencies", "equally likely outcomes", "assigning probabilities", "probability"]):
        if has_terms(text, ["relative frequencies"]):
            return (
                "A coin is tossed 50 times and lands heads 31 times. Estimate the probability of heads from the relative frequency.",
                ["Use frequency divided by total trials.", "Write the estimate as a decimal or fraction.", "State that it is an estimate."],
                ["Estimated probability = 31/50.", "31/50 = 0.62.", "Answer: estimated probability of heads is 0.62."],
                ["Relative frequency uses observed results.", "The answer is an estimate, not an exact value.", "The total number of trials is 50."],
            )
        return (
            "A fair die is rolled once. Find the probability of getting a number greater than 4.",
            ["Count the favourable outcomes.", "Count all equally likely outcomes.", "Write the probability as a fraction."],
            ["Numbers greater than 4 are 5 and 6.", "There are 2 favourable outcomes out of 6 equally likely outcomes.", "P(number > 4) = 2/6 = 1/3.", "Answer: 1/3."],
            ["Equal likelihood means simple counting works.", "The probability is reduced to simplest form.", "The sample space has 6 outcomes."],
        )
    if has_terms(text, ["using algebraic methods", "equal roots", "distinct real roots", "no real roots"]):
        return (
            "Two curves intersect when x^2 - 4x + 5 = 0. Use the discriminant to decide whether the curves meet.",
            ["Write the intersection equation.", "Calculate the discriminant.", "Interpret the sign of the discriminant in context."],
            ["For x^2 - 4x + 5 = 0, a=1, b=-4, c=5.", "b^2 - 4ac = 16 - 20 = -4.", "The discriminant is negative.", "Answer: there are no real intersections."],
            ["The discriminant links algebra to graph intersections.", "No real roots means no real intersection points.", "The conclusion is stated in context."],
        )
    if has_terms(text, ["translation of circles", "translated circle"]):
        return (
            "The circle x^2 + y^2 = 9 is translated 4 units right and 2 units down. Write the new equation.",
            ["Move the centre by the translation vector.", "Keep the radius the same.", "Write the completed-square form."],
            ["The original centre is (0,0) and radius is 3.", "After translation the centre is (4,-2).", "New equation: (x-4)^2 + (y+2)^2 = 9.", "Answer: (x-4)^2 + (y+2)^2 = 9."],
            ["A translation changes the centre, not the radius.", "The y-coordinate sign changes correctly.", "The final equation matches the new centre."],
        )
    if has_terms(text, ["surd", "surds", "rationalisation"]):
        return (
            "Simplify sqrt(72) + sqrt(18), then rationalise 5/sqrt(2).",
            ["Write each surd using square factors.", "Collect like surds.", "Multiply numerator and denominator by sqrt(2)."],
            ["sqrt(72) = sqrt(36 x 2) = 6sqrt(2).", "sqrt(18) = sqrt(9 x 2) = 3sqrt(2), so the sum is 9sqrt(2).", "5/sqrt(2) = 5sqrt(2)/2.", "Answer: 9sqrt(2) and 5sqrt(2)/2."],
            ["Square factors are taken outside the root.", "Only like surds are combined.", "The denominator is rational after rationalising."],
        )
    if has_terms(text, ["indices", "index", "rational exponent", "rational exponents"]):
        return (
            "Simplify a^(3/2) x a^(1/2), then write a^(1/2) as a surd.",
            ["Use the index law for multiplying powers with the same base.", "Add the exponents.", "Translate the one-half power into surd notation."],
            ["a^(3/2) x a^(1/2) = a^(3/2 + 1/2).", "3/2 + 1/2 = 4/2 = 2.", "So the product is a^2.", "a^(1/2) = sqrt(a)."],
            ["The base stays as a.", "Only exponents are added for multiplication.", "The rational exponent is converted to the matching root."],
        )
    if has_terms(text, ["discriminant"]):
        return (
            "Use the discriminant to decide how many real roots x^2 - 4x + 5 = 0 has.",
            ["Identify a, b and c.", "Calculate b^2 - 4ac.", "Use the sign of the discriminant."],
            ["Here a=1, b=-4 and c=5.", "b^2 - 4ac = (-4)^2 - 4(1)(5) = 16 - 20 = -4.", "The discriminant is negative.", "Answer: the equation has no real roots."],
            ["The negative b value is squared correctly.", "A negative discriminant means no real roots.", "The conclusion is about roots, not turning points."],
        )
    if has_terms(text, ["completing the square", "complete the square"]):
        return (
            "Write x^2 + 6x - 1 in completed-square form.",
            ["Halve the coefficient of x.", "Add and subtract the square of that half.", "Simplify the constant term."],
            ["Half of 6 is 3.", "x^2 + 6x - 1 = (x+3)^2 - 9 - 1.", "So x^2 + 6x - 1 = (x+3)^2 - 10.", "Answer: (x+3)^2 - 10."],
            ["The bracket uses half the x coefficient.", "The extra 9 is subtracted back.", "Expanding the answer checks it."],
        )
    if has_terms(text, ["factorisation", "factorization"]) and has_terms(text, ["quadratic", "quadratics"]):
        return (
            "Factorise 2x^2 + x - 6.",
            ["Find two terms whose product matches 2x^2 and -6.", "Split the middle term.", "Factorise by grouping."],
            ["2x^2 + x - 6 = 2x^2 + 4x - 3x - 6.", "Group: 2x(x+2) - 3(x+2).", "Take out the common bracket.", "Answer: (2x-3)(x+2)."],
            ["Expanding gives 2x^2 + x - 6.", "The signs in the brackets are correct.", "Both factors are included."],
        )
    if has_terms(text, ["quadratic function", "quadratic functions", "graphs", "vertex", "line of symmetry"]):
        return (
            "For y = (x - 3)^2 + 2, state the vertex and line of symmetry.",
            ["Recognise completed-square form.", "Read the horizontal shift carefully.", "The line of symmetry passes through the vertex."],
            ["The minimum point is at x = 3.", "The y-value there is 2.", "So the vertex is (3, 2).", "Answer: vertex (3, 2), line of symmetry x = 3."],
            ["The sign inside the bracket reverses for the x-coordinate.", "The line of symmetry is vertical.", "The answer describes the graph, not just the equation."],
        )
    if has_terms(text, ["divided", "division"]) and has_terms(text, ["polynomial", "polynomials"]):
        return (
            "Find the remainder when f(x)=x^3-4x^2+x+6 is divided by x-2.",
            ["Use the Remainder Theorem.", "Evaluate f(2).", "State the remainder."],
            ["For division by x-2, use x=2.", "f(2)=8-16+2+6.", "f(2)=0.", "Answer: the remainder is 0."],
            ["The divisor x-2 gives x=2.", "The value of f(2) is the remainder.", "A zero remainder means exact division."],
        )
    if has_terms(text, ["factor theorem", "remainder theorem"]):
        if has_terms(text, ["application"]):
            return (
                "For f(x)=x^3+2x^2-x-2, use the Factor Theorem to check whether x+2 is a factor.",
                ["Use x+2 = 0 to find the test value.", "Evaluate f(-2).", "Interpret a zero remainder."],
                ["For x+2, test x = -2.", "f(-2)=-8+8+2-2.", "f(-2)=0.", "Therefore x+2 is a factor of f(x)."],
                ["The test value is -2.", "A zero value means factor.", "The conclusion names x+2."],
            )
        return (
            "For f(x)=x^3-4x^2+x+6, use the Factor Theorem to check whether x-2 is a factor.",
            ["Use x-2 = 0 to find the test value.", "Evaluate f(2).", "Interpret a zero remainder."],
            ["For x-2, test x = 2.", "f(2)=8-16+2+6.", "f(2)=0.", "Therefore x-2 is a factor of f(x)."],
            ["The test value has the correct sign.", "A zero value means factor, not just root by guesswork.", "The conclusion names the factor."],
        )
    if has_terms(text, ["circle", "circles"]):
        return (
            "Write the centre and radius of (x-3)^2 + (y+2)^2 = 25.",
            ["Compare with (x-a)^2 + (y-b)^2 = r^2.", "Read the centre signs carefully.", "Square-root the right-hand side."],
            ["The centre is (3, -2).", "r^2 = 25.", "r = 5.", "Answer: centre (3, -2), radius 5."],
            ["The y-coordinate sign is not copied as +2.", "The radius is positive.", "The equation is in completed-square circle form."],
        )
    if has_terms(text, ["trigonometry", "radian", "radians", "sine", "cosine"]):
        return (
            "Convert pi/3 radians to degrees, then find the exact value of sin(pi/3).",
            ["Use pi radians = 180 degrees.", "Convert the angle.", "Use the exact trig value."],
            ["pi/3 radians = 180/3 degrees.", "So the angle is 60 degrees.", "sin(pi/3)=sin 60 degrees.", "Answer: sqrt(3)/2."],
            ["Radian conversion uses pi radians = 180 degrees.", "The exact value is not rounded.", "The angle is in the first quadrant."],
        )
    if has_terms(text, ["sequence", "sequences", "series", "arithmetic", "geometric"]):
        return (
            "An arithmetic sequence has first term 7 and common difference 4. Find the 12th term and the sum of the first 12 terms.",
            ["Use a_n = a + (n-1)d.", "Substitute n = 12.", "Use the arithmetic-series sum formula."],
            ["a_12 = 7 + 11 x 4 = 51.", "S_12 = 12/2 x (7 + 51).", "S_12 = 6 x 58 = 348.", "Answer: 12th term 51; sum 348."],
            ["n-1 is used in the nth-term formula.", "The first and last terms are used in the sum.", "The answer separates term and sum."],
        )
    if has_terms(text, ["coordinate", "coordinates", "straight line", "gradient", "perpendicular"]) and not has_terms(
        text,
        [
            "acceleration",
            "derivative",
            "differentiation",
            "displacement",
            "motion",
            "speed",
            "stationary",
            "tangent",
            "velocity",
        ],
    ):
        return (
            "Find the equation of the line through (2, 5) with gradient 3.",
            ["Start with y = mx + c.", "Substitute the gradient.", "Use the point to find c."],
            ["y = 3x + c.", "Using (2, 5): 5 = 3(2) + c.", "c = -1.", "Answer: y = 3x - 1."],
            ["The gradient is the coefficient of x.", "The point is substituted into the line equation.", "The final equation is in terms of x and y."],
        )
    if has_terms(text, ["derivative", "differentiation", "tangent", "gradient", "stationary"]):
        return (
            "For y = 3x^2 - 4x + 1, find dy/dx and the gradient of the tangent when x = 2.",
            ["Differentiate term by term.", "Substitute x = 2 into the derivative.", "State the gradient clearly."],
            ["dy/dx = 6x - 4.", "When x = 2, dy/dx = 6(2) - 4.", "The gradient is 8.", "Answer: dy/dx = 6x - 4; tangent gradient = 8."],
            ["The constant differentiates to 0.", "The x-value is substituted after differentiating.", "The gradient is a number."],
        )
    if has_terms(text, ["integration", "integral", "trapezium", "area under"]):
        if has_terms(text, ["area", "curve", "x-axis"]) and number % 2:
            return (
                "Find the area under y = 2x from x = 1 to x = 4.",
                ["Set up the definite integral.", "Find an antiderivative.", "Subtract lower limit from upper limit."],
                ["Area = integral from 1 to 4 of 2x dx.", "An antiderivative of 2x is x^2.", "Area = 4^2 - 1^2 = 16 - 1.", "Answer: 15 square units."],
                ["The limits are used in the correct order.", "The antiderivative is checked by differentiating.", "Area is positive."],
            )
        return (
            "Find the indefinite integral of 6x^2 - 4x with respect to x.",
            ["Increase each power by 1.", "Divide by the new power.", "Add the constant of integration."],
            ["The integral of 6x^2 is 2x^3.", "The integral of -4x is -2x^2.", "Add the constant C.", "Answer: 2x^3 - 2x^2 + C."],
            ["The power rule is reversed.", "The constant C is included.", "Differentiating the answer checks the integrand."],
        )
    if has_terms(text, ["logarithm", "logarithms", "exponential", "exponentials"]):
        return (
            "Solve 3^x = 81, then write the result using logarithm notation.",
            ["Write 81 as a power of 3.", "Equate the powers.", "Connect the answer to log notation."],
            ["81 = 3^4.", "So 3^x = 3^4 gives x = 4.", "In log form, log_3 81 = 4.", "Answer: x = 4."],
            ["The base is 3.", "The logarithm statement matches the exponential statement.", "The answer is checked by substitution."],
        )
    if has_terms(text, ["binomial", "bernoulli"]):
        if not has_terms(text, ["mean", "variance", "standard deviation"]):
            return (
                "Let X ~ B(5, 0.4). Find P(X=2).",
                ["Use the binomial probability formula.", "Substitute n=5, p=0.4 and x=2.", "Keep the combination term."],
                ["P(X=2)=C(5,2)(0.4)^2(0.6)^3.", "C(5,2)=10.", "P(X=2)=10 x 0.16 x 0.216.", "Answer: P(X=2)=0.3456."],
                ["The power of 0.4 matches the number of successes.", "The power of 0.6 matches failures.", "The combination counts arrangements."],
            )
        return (
            "Let X ~ B(10, 0.3). Find E(X) and Var(X).",
            ["Use E(X)=np.", "Use Var(X)=np(1-p).", "Substitute n=10 and p=0.3."],
            ["E(X)=10 x 0.3 = 3.", "Var(X)=10 x 0.3 x 0.7.", "Var(X)=2.1.", "Answer: E(X)=3 and Var(X)=2.1."],
            ["The value of 1-p is 0.7.", "Expectation and variance use different formulae.", "X is identified as binomial."],
        )
    if has_terms(text, ["random variable", "variance", "standard deviation"]):
        if has_terms(text, ["sum", "independent"]):
            return (
                "A random variable X has E(X)=4 and Var(X)=1.5. An independent random variable Y has E(Y)=3 and Var(Y)=2. Find E(X+Y) and Var(X+Y).",
                ["Add expectations.", "Use independence to add variances.", "State both values clearly."],
                ["E(X+Y)=E(X)+E(Y)=4+3=7.", "Because X and Y are independent, Var(X+Y)=Var(X)+Var(Y).", "Var(X+Y)=1.5+2=3.5.", "Answer: E(X+Y)=7 and Var(X+Y)=3.5."],
                ["Independence is needed for adding variances.", "Expectation is linear.", "Do not add standard deviations."],
            )
        if has_terms(text, ["spread"]):
            return (
                "A random variable X has P(X=0)=0.2, P(X=1)=0.5 and P(X=2)=0.3. Find E(X) and Var(X).",
                ["Find E(X).", "Find E(X^2).", "Use Var(X)=E(X^2)-[E(X)]^2."],
                ["E(X)=0(0.2)+1(0.5)+2(0.3)=1.1.", "E(X^2)=0^2(0.2)+1^2(0.5)+2^2(0.3)=1.7.", "Var(X)=1.7-1.1^2.", "Answer: Var(X)=0.49."],
                ["Variance measures spread.", "E(X^2) is not the same as [E(X)]^2.", "The variance is non-negative."],
            )
        return (
            "A random variable X has P(X=0)=0.2, P(X=1)=0.5 and P(X=2)=0.3. Find E(X).",
            ["Multiply each value by its probability.", "Add the products.", "Check probabilities add to 1."],
            ["The probabilities add to 0.2 + 0.5 + 0.3 = 1.", "E(X) = 0(0.2) + 1(0.5) + 2(0.3).", "E(X) = 0 + 0.5 + 0.6 = 1.1.", "Answer: E(X) = 1.1."],
            ["Each x-value is weighted by its probability.", "Probabilities sum to 1.", "Expectation is not necessarily a possible value of X."],
        )
    if has_terms(text, ["displacement", "speed", "velocity", "acceleration", "motion"]) and not has_terms(
        text,
        ["force", "forces", "newton", "momentum", "impulse"],
    ):
        if has_terms(text, ["average speed"]):
            return (
                "A particle travels 120 m in 8 s. Find its average speed.",
                ["Use average speed = distance / time.", "Substitute the distance and time.", "Give the unit."],
                ["Average speed = 120 / 8.", "120 / 8 = 15.", "Answer: 15 m/s.", "This is an average over the whole journey."],
                ["Distance is in metres.", "Time is in seconds.", "The unit is m/s."],
            )
        return (
            "A particle starts from rest and accelerates at 2 m/s^2 for 5 s. Find its final velocity.",
            ["Use v = u + at.", "Substitute u=0, a=2 and t=5.", "Give the unit."],
            ["v = u + at.", "v = 0 + 2 x 5.", "v = 10.", "Answer: 10 m/s."],
            ["Starts from rest means u=0.", "Acceleration is multiplied by time.", "Velocity has unit m/s."],
        )
    if has_terms(text, ["conservation of momentum"]):
        return (
            "A 2 kg particle moving at 5 m/s collides with a 3 kg particle at rest. After the collision, the 2 kg particle moves at 1 m/s in the same direction. Find the speed of the 3 kg particle.",
            ["Write total momentum before the collision.", "Write total momentum after the collision.", "Equate the two totals and solve."],
            ["Momentum before = 2 x 5 + 3 x 0 = 10.", "Momentum after = 2 x 1 + 3v = 2 + 3v.", "Conservation gives 10 = 2 + 3v.", "Answer: v = 8/3 m/s."],
            ["Both particles are included in the system.", "Directions are kept consistent.", "The answer is a speed in m/s."],
        )
    if has_terms(text, ["direct impact", "fixed surface"]):
        return (
            "A 0.5 kg particle hits a smooth fixed wall perpendicularly at 6 m/s and rebounds at 4 m/s. Taking the original direction as positive, find the change in momentum.",
            ["Write the initial momentum with the chosen sign.", "Write the final momentum after rebound.", "Calculate final momentum minus initial momentum."],
            ["Initial momentum = 0.5 x 6 = 3 kg m/s.", "Final velocity is -4 m/s, so final momentum = 0.5 x (-4) = -2 kg m/s.", "Change in momentum = -2 - 3 = -5 kg m/s.", "Answer: change in momentum = -5 kg m/s."],
            ["The rebound velocity has the opposite sign.", "Change means final minus initial.", "The fixed wall is not assigned a velocity."],
        )
    if has_terms(text, ["impulse"]):
        return (
            "A particle has momentum 12 kg m/s before an impact and 5 kg m/s afterwards in the same direction. Find the impulse on the particle.",
            ["Use impulse = change in momentum.", "Subtract initial momentum from final momentum.", "State the sign and unit."],
            ["Impulse = final momentum - initial momentum.", "Impulse = 5 - 12.", "Impulse = -7.", "Answer: impulse = -7 N s."],
            ["The sign shows the impulse acts opposite to the original direction.", "N s is equivalent to kg m/s.", "Use change in momentum, not total momentum."],
        )
    if has_terms(text, ["concept of momentum", "momentum = mv"]):
        return (
            "A 3 kg particle moves in a straight line at 4 m/s. Find its momentum.",
            ["Use p = mv.", "Substitute the mass and velocity.", "Give the vector unit."],
            ["p = mv.", "p = 3 x 4.", "p = 12.", "Answer: momentum = 12 kg m/s in the direction of motion."],
            ["Mass is in kg.", "Velocity is in m/s.", "Momentum includes direction."],
        )
    if has_terms(text, ["force", "forces", "newton", "motion", "velocity", "acceleration", "momentum", "impulse"]):
        return (
            "A 4 kg particle accelerates at 3 m/s^2. Find the resultant force.",
            ["Use Newton's second law.", "Substitute mass and acceleration.", "Give the unit."],
            ["F = ma.", "F = 4 x 3.", "F = 12.", "Answer: resultant force = 12 N."],
            ["Mass is in kg.", "Acceleration is in m/s^2.", "The force unit is newtons."],
        )
    return (
        "Solve x^2 - 5x + 6 = 0 and check both roots.",
        ["Factorise the quadratic.", "Set each factor equal to zero.", "Substitute the roots back into the equation."],
        ["x^2 - 5x + 6 = (x - 2)(x - 3).", "x - 2 = 0 or x - 3 = 0.", "So x = 2 or x = 3.", "Both roots make x^2 - 5x + 6 equal to 0."],
        ["Both roots are included.", "The signs in the factors are correct.", "Substitution checks the answer."],
    )


def mathematics_specialist_example_zh(
    text: str,
    number: int,
) -> tuple[str, list[str], list[str], list[str]]:
    if has_terms(text, ["surd", "surds", "rationalisation"]):
        return (
            "化简 sqrt(72) + sqrt(18)，并把 5/sqrt(2) 的分母有理化。",
            ["先把根号内拆成平方因数乘积。", "合并同类根式。", "分子分母同乘 sqrt(2)。"],
            ["sqrt(72)=sqrt(36×2)=6sqrt(2)。", "sqrt(18)=sqrt(9×2)=3sqrt(2)，所以和为 9sqrt(2)。", "5/sqrt(2)=5sqrt(2)/2。", "答案：9sqrt(2)，5sqrt(2)/2。"],
            ["平方因数要移到根号外。", "只有同类根式才能合并。", "分母有理化后分母不再含根号。"],
        )
    if has_terms(text, ["indices", "index", "rational exponent", "rational exponents"]):
        return (
            "化简 a^(3/2) × a^(1/2)，并把 a^(1/2) 写成根式。",
            ["同底数幂相乘，指数相加。", "计算 3/2 + 1/2。", "把 1/2 次幂改写成平方根。"],
            ["a^(3/2) × a^(1/2) = a^(3/2+1/2)。", "3/2+1/2=2。", "所以乘积为 a^2。", "a^(1/2)=sqrt(a)。"],
            ["底数 a 不变。", "乘法时加指数，不是乘指数。", "有理指数要能和根式互相转换。"],
        )
    if has_terms(text, ["discriminant"]):
        return (
            "用判别式判断方程 x^2 - 4x + 5 = 0 有几个实根。",
            ["找出 a、b、c。", "计算 b^2 - 4ac。", "根据判别式正负判断实根情况。"],
            ["这里 a=1，b=-4，c=5。", "b^2 - 4ac = (-4)^2 - 4×1×5 = 16 - 20 = -4。", "判别式小于 0。", "答案：没有实根。"],
            ["负的 b 平方时要变正。", "判别式小于 0 表示没有实根。", "结论说的是根的情况，不是顶点。"],
        )
    if has_terms(text, ["completing the square", "complete the square"]):
        return (
            "把 x^2 + 6x - 1 写成配方形式。",
            ["把 x 的系数 6 减半。", "加上再减去这个数的平方。", "整理常数项。"],
            ["6 的一半是 3。", "x^2 + 6x - 1 = (x+3)^2 - 9 - 1。", "所以 x^2 + 6x - 1 = (x+3)^2 - 10。", "答案：(x+3)^2 - 10。"],
            ["括号里用 x 系数的一半。", "补出的 9 要减回去。", "展开答案可以检查。"],
        )
    if has_terms(text, ["factorisation", "factorization"]) and has_terms(text, ["quadratic", "quadratics"]):
        return (
            "因式分解 2x^2 + x - 6。",
            ["把中间项拆成两项。", "分组提取公因式。", "再提取公共括号。"],
            ["2x^2 + x - 6 = 2x^2 + 4x - 3x - 6。", "分组得 2x(x+2) - 3(x+2)。", "提取公共括号。", "答案：(2x-3)(x+2)。"],
            ["展开后应回到 2x^2 + x - 6。", "括号中的符号不能写反。", "两个因式都要写出。"],
        )
    if has_terms(text, ["quadratic function", "quadratic functions", "graphs", "vertex", "line of symmetry"]):
        return (
            "对于 y = (x - 3)^2 + 2，写出顶点和对称轴。",
            ["识别配方形式。", "注意括号内符号对应水平平移。", "对称轴经过顶点。"],
            ["最小点的 x 坐标为 3。", "对应 y 值为 2。", "所以顶点是 (3,2)。", "答案：顶点 (3,2)，对称轴 x=3。"],
            ["括号里的符号和顶点 x 坐标相反。", "对称轴是竖直直线。", "答案要描述图像特征。"],
        )
    if has_terms(text, ["divided", "division"]) and has_terms(text, ["polynomial", "polynomials"]):
        return (
            "求 f(x)=x^3-4x^2+x+6 除以 x-2 的余数。",
            ["使用余式定理。", "计算 f(2)。", "写出余数。"],
            ["除以 x-2 时，取 x=2。", "f(2)=8-16+2+6。", "f(2)=0。", "答案：余数为 0。"],
            ["x-2 对应 x=2。", "f(2) 就是余数。", "余数为 0 表示整除。"],
        )
    if has_terms(text, ["factor theorem", "remainder theorem"]):
        if has_terms(text, ["application"]):
            return (
                "设 f(x)=x^3+2x^2-x-2，用因式定理判断 x+2 是否为 f(x) 的因式。",
                ["由 x+2=0 得到检验值 x=-2。", "计算 f(-2)。", "余数为 0 时说明是因式。"],
                ["检验 x=-2。", "f(-2)=-8+8+2-2。", "f(-2)=0。", "所以 x+2 是 f(x) 的因式。"],
                ["检验值应为 -2。", "f(-2)=0 才能推出因式关系。", "结论要写清 x+2。"],
            )
        return (
            "设 f(x)=x^3-4x^2+x+6，用因式定理判断 x-2 是否为 f(x) 的因式。",
            ["由 x-2=0 得到检验值 x=2。", "计算 f(2)。", "余数为 0 时说明是因式。"],
            ["检验 x=2。", "f(2)=8-16+2+6。", "f(2)=0。", "所以 x-2 是 f(x) 的因式。"],
            ["检验值的正负号不能弄反。", "f(2)=0 才能推出 x-2 是因式。", "结论要写清楚对应因式。"],
        )
    if has_terms(text, ["circle", "circles"]):
        return (
            "写出圆 (x-3)^2 + (y+2)^2 = 25 的圆心和半径。",
            ["与 (x-a)^2+(y-b)^2=r^2 对照。", "注意括号里的符号和圆心坐标相反。", "对右边开平方求半径。"],
            ["圆心为 (3,-2)。", "r^2=25。", "r=5。", "答案：圆心 (3,-2)，半径 5。"],
            ["y 坐标不能误写成 +2。", "半径取正数。", "方程已经是圆的标准形式。"],
        )
    if has_terms(text, ["trigonometry", "radian", "radians", "sine", "cosine"]):
        return (
            "把 pi/3 弧度化成角度，并写出 sin(pi/3) 的精确值。",
            ["使用 pi 弧度 = 180°。", "先完成角度换算。", "再写出特殊角三角函数值。"],
            ["pi/3 弧度 = 180°/3。", "所以角度为 60°。", "sin(pi/3)=sin60°。", "答案：sqrt(3)/2。"],
            ["弧度和角度的换算关系要正确。", "精确值不要写成小数近似。", "60° 在第一象限，正弦为正。"],
        )
    if has_terms(text, ["sequence", "sequences", "series", "arithmetic", "geometric"]):
        return (
            "等差数列首项为 7，公差为 4。求第 12 项和前 12 项和。",
            ["用 a_n=a+(n-1)d 求第 n 项。", "代入 n=12。", "用等差数列求和公式。"],
            ["a_12=7+11×4=51。", "S_12=12/2×(7+51)。", "S_12=6×58=348。", "答案：第 12 项为 51，前 12 项和为 348。"],
            ["第 n 项公式里是 n-1。", "求和要用首项和末项。", "第 12 项和前 12 项和不要混淆。"],
        )
    if has_terms(text, ["coordinate", "coordinates", "straight line", "gradient", "perpendicular"]) and not has_terms(
        text,
        [
            "acceleration",
            "derivative",
            "differentiation",
            "displacement",
            "motion",
            "speed",
            "stationary",
            "tangent",
            "velocity",
        ],
    ):
        return (
            "求过点 (2,5)、斜率为 3 的直线方程。",
            ["从 y=mx+c 开始。", "代入斜率 m=3。", "用点 (2,5) 求 c。"],
            ["y=3x+c。", "代入 (2,5)：5=3×2+c。", "c=-1。", "答案：y=3x-1。"],
            ["斜率是 x 的系数。", "点坐标要代入直线方程。", "最终答案要含 x 和 y。"],
        )
    if has_terms(text, ["derivative", "differentiation", "tangent", "gradient", "stationary"]):
        return (
            "已知 y = 3x^2 - 4x + 1，求 dy/dx，并求 x = 2 时切线的斜率。",
            ["逐项求导。", "把 x = 2 代入导函数。", "清楚写出切线斜率。"],
            ["dy/dx = 6x - 4。", "当 x = 2 时，dy/dx = 6(2) - 4。", "切线斜率为 8。", "答案：dy/dx = 6x - 4，切线斜率 = 8。"],
            ["常数项求导后为 0。", "先求导，再代入 x 值。", "斜率最后应是一个数。"],
        )
    if has_terms(text, ["integration", "integral", "trapezium", "area under"]):
        if has_terms(text, ["area", "curve", "x-axis"]) and number % 2:
            return (
                "求 y = 2x 在 x=1 到 x=4 之间曲线下方的面积。",
                ["写成定积分。", "先求一个原函数。", "用上限结果减下限结果。"],
                ["面积 = ∫_1^4 2x dx。", "2x 的一个原函数是 x^2。", "面积 = 4^2 - 1^2 = 16 - 1。", "答案：15 平方单位。"],
                ["上下限顺序不能反。", "原函数可通过求导检查。", "面积应为正。"],
            )
        return (
            "求 ∫(6x^2 - 4x) dx。",
            ["每一项的次数加 1。", "除以新的次数。", "补上积分常数。"],
            ["∫6x^2 dx = 2x^3。", "∫-4x dx = -2x^2。", "不定积分要加 C。", "答案：2x^3 - 2x^2 + C。"],
            ["这是求导规则的反向使用。", "不要漏写 C。", "把答案再求导可以检查。"],
        )
    if has_terms(text, ["logarithm", "logarithms", "exponential", "exponentials"]):
        return (
            "解方程 3^x = 81，并用 log 记号写出同一个关系。",
            ["把 81 写成 3 的幂。", "比较指数。", "把指数式改写成 log 形式。"],
            ["81 = 3^4。", "所以 3^x = 3^4，得到 x = 4。", "用 log 记号表示为 log_3 81 = 4。", "答案：x = 4。"],
            ["底数是 3。", "log 形式和指数形式要表达同一件事。", "代回 3^4 = 81 可检查。"],
        )
    if has_terms(text, ["binomial", "bernoulli"]):
        if not has_terms(text, ["mean", "variance", "standard deviation"]):
            return (
                "设 X ~ B(5, 0.4)，求 P(X=2)。",
                ["使用二项分布概率公式。", "代入 n=5、p=0.4、x=2。", "保留组合数项。"],
                ["P(X=2)=C(5,2)(0.4)^2(0.6)^3。", "C(5,2)=10。", "P(X=2)=10×0.16×0.216。", "答案：P(X=2)=0.3456。"],
                ["0.4 的指数对应成功次数。", "0.6 的指数对应失败次数。", "组合数表示排列方式数量。"],
            )
        return (
            "设 X ~ B(10, 0.3)，求 E(X) 和 Var(X)。",
            ["使用 E(X)=np。", "使用 Var(X)=np(1-p)。", "代入 n=10，p=0.3。"],
            ["E(X)=10×0.3=3。", "Var(X)=10×0.3×0.7。", "Var(X)=2.1。", "答案：E(X)=3，Var(X)=2.1。"],
            ["1-p=0.7。", "期望和方差公式不同。", "先确认 X 服从二项分布。"],
        )
    if has_terms(text, ["random variable", "variance", "standard deviation"]):
        if has_terms(text, ["sum", "independent"]):
            return (
                "已知随机变量 X 的 E(X)=4、Var(X)=1.5，独立随机变量 Y 的 E(Y)=3、Var(Y)=2。求 E(X+Y) 和 Var(X+Y)。",
                ["期望相加。", "独立时方差相加。", "分别写出两个结果。"],
                ["E(X+Y)=E(X)+E(Y)=4+3=7。", "因为 X 和 Y 独立，Var(X+Y)=Var(X)+Var(Y)。", "Var(X+Y)=1.5+2=3.5。", "答案：E(X+Y)=7，Var(X+Y)=3.5。"],
                ["方差相加需要独立条件。", "期望具有线性性质。", "不要把标准差直接相加。"],
            )
        if has_terms(text, ["spread"]):
            return (
                "离散随机变量 X 满足 P(X=0)=0.2，P(X=1)=0.5，P(X=2)=0.3。求 E(X) 和 Var(X)。",
                ["先求 E(X)。", "再求 E(X^2)。", "使用 Var(X)=E(X^2)-[E(X)]^2。"],
                ["E(X)=0×0.2+1×0.5+2×0.3=1.1。", "E(X^2)=0^2×0.2+1^2×0.5+2^2×0.3=1.7。", "Var(X)=1.7-1.1^2。", "答案：Var(X)=0.49。"],
                ["方差衡量离散程度。", "E(X^2) 不等于 [E(X)]^2。", "方差不能为负。"],
            )
        return (
            "离散随机变量 X 满足 P(X=0)=0.2，P(X=1)=0.5，P(X=2)=0.3。求 E(X)。",
            ["每个取值乘以对应概率。", "把乘积相加。", "先检查概率总和是否为 1。"],
            ["概率总和为 0.2 + 0.5 + 0.3 = 1。", "E(X) = 0(0.2) + 1(0.5) + 2(0.3)。", "E(X) = 0 + 0.5 + 0.6 = 1.1。", "答案：E(X)=1.1。"],
            ["每个 X 取值都要按概率加权。", "概率总和必须为 1。", "期望值不一定是 X 的实际取值。"],
        )
    if has_terms(text, ["displacement", "speed", "velocity", "acceleration", "motion"]) and not has_terms(
        text,
        ["force", "forces", "newton", "momentum", "impulse"],
    ):
        if has_terms(text, ["average speed"]):
            return (
                "一个质点 8 秒内运动 120 m。求平均速度。",
                ["使用平均速度 = 路程 / 时间。", "代入路程和时间。", "写出单位。"],
                ["平均速度 = 120 / 8。", "120 / 8 = 15。", "答案：15 m/s。", "这是整个过程的平均速度。"],
                ["路程单位是 m。", "时间单位是 s。", "速度单位是 m/s。"],
            )
        return (
            "一个质点从静止开始，以 2 m/s^2 加速 5 s。求末速度。",
            ["使用 v = u + at。", "代入 u=0、a=2、t=5。", "写出单位。"],
            ["v = u + at。", "v = 0 + 2×5。", "v = 10。", "答案：10 m/s。"],
            ["从静止开始表示 u=0。", "加速度要乘以时间。", "速度单位是 m/s。"],
        )
    if has_terms(text, ["conservation of momentum"]):
        return (
            "一个 2 kg 质点以 5 m/s 撞上一个静止的 3 kg 质点。碰后 2 kg 质点仍沿原方向以 1 m/s 运动。求 3 kg 质点碰后的速度。",
            ["写出碰前系统总动量。", "写出碰后系统总动量。", "令碰前总动量等于碰后总动量并求解。"],
            ["碰前动量 = 2×5 + 3×0 = 10。", "碰后动量 = 2×1 + 3v = 2 + 3v。", "由动量守恒得 10 = 2 + 3v。", "答案：v = 8/3 m/s。"],
            ["两个质点都要计入同一系统。", "方向约定要保持一致。", "速度单位是 m/s。"],
        )
    if has_terms(text, ["direct impact", "fixed surface"]):
        return (
            "一个 0.5 kg 质点垂直撞向光滑固定墙，碰前速度为 6 m/s，碰后以 4 m/s 反向弹回。取原方向为正，求动量变化。",
            ["写出碰前动量并保留方向符号。", "写出反弹后的动量。", "用末动量减初动量。"],
            ["初动量 = 0.5×6 = 3 kg m/s。", "反弹后速度为 -4 m/s，所以末动量 = 0.5×(-4) = -2 kg m/s。", "动量变化 = -2 - 3 = -5 kg m/s。", "答案：动量变化 = -5 kg m/s。"],
            ["反弹速度方向相反，所以符号为负。", "变化量是末值减初值。", "固定墙不需要赋予速度。"],
        )
    if has_terms(text, ["impulse"]):
        return (
            "一个质点碰前动量为 12 kg m/s，碰后仍沿同一直线方向动量为 5 kg m/s。求质点受到的冲量。",
            ["使用冲量 = 动量变化。", "用末动量减初动量。", "写出符号和单位。"],
            ["冲量 = 末动量 - 初动量。", "冲量 = 5 - 12。", "冲量 = -7。", "答案：冲量 = -7 N s。"],
            ["负号表示冲量方向与原运动方向相反。", "N s 与 kg m/s 等价。", "用的是动量变化，不是动量总和。"],
        )
    if has_terms(text, ["concept of momentum", "momentum = mv"]):
        return (
            "一个 3 kg 质点沿直线以 4 m/s 运动。求它的动量。",
            ["使用 p = mv。", "代入质量和速度。", "写出带方向含义的单位。"],
            ["p = mv。", "p = 3×4。", "p = 12。", "答案：动量 = 12 kg m/s，方向沿质点运动方向。"],
            ["质量单位是 kg。", "速度单位是 m/s。", "动量包含方向。"],
        )
    if has_terms(text, ["force", "forces", "newton", "motion", "velocity", "acceleration", "momentum", "impulse"]):
        return (
            "一个质量为 4 kg 的质点加速度为 3 m/s^2。求合力大小。",
            ["使用牛顿第二定律。", "代入质量和加速度。", "写出力的单位。"],
            ["F = ma。", "F = 4 × 3。", "F = 12。", "答案：合力 = 12 N。"],
            ["质量单位是 kg。", "加速度单位是 m/s^2。", "力的单位是 N。"],
        )
    return (
        "解方程 x^2 - 5x + 6 = 0，并检查两个根。",
        ["先因式分解二次式。", "令每个因式等于 0。", "把根代回原式检查。"],
        ["x^2 - 5x + 6 = (x - 2)(x - 3)。", "x - 2 = 0 或 x - 3 = 0。", "所以 x = 2 或 x = 3。", "两个根代回后都使原式等于 0。"],
        ["两个根都要写出。", "因式中的符号不能写反。", "代回检查能发现粗心错误。"],
    )
