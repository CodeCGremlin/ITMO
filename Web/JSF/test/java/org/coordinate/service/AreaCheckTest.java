package org.coordinate.service;

import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;



public class AreaCheckTest {

    private AreaCheck areaCheck;

    @Before
    public void setUp() {
        areaCheck = new AreaCheck();
    }

    @Test
    public void testCircleInside() {
        assertTrue("Точка (1.0, 1.0) внутри круга с r=2",
                areaCheck.checkHit(1.0, 1.0, 2.0));
        assertTrue("Центр (0.0, 0.0) всегда внутри",
                areaCheck.checkHit(0.0, 0.0, 2.0));
    }

    @Test
    public void testCircleOutside() {Invoke-Item "build.ant/test-reports/html/index.html"
        assertFalse("Точка (1.5, 1.5) вне круга с r=2 (4.5 > 4)",
                areaCheck.checkHit(1.5, 1.5, 2.0));
    }

    @Test
    public void testSquareInside() {
        assertTrue("Точка (-1.0, 1.0) внутри прямоугольника с r=2",
                areaCheck.checkHit(-1.0, 1.0, 2.0));
        assertTrue("Точка (-1.9, 0.1) у границы прямоугольника с r=2",
                areaCheck.checkHit(-1.9, 0.1, 2.0));
    }

    @Test
    public void testSquareOutside() {
        assertFalse("X=-2.5 ≤ -R=−2  вне прямоугольника",
                areaCheck.checkHit(-2.5, 1.0, 2.0));
        assertFalse("Y=2.5 > R=2  вне прямоугольника",
                areaCheck.checkHit(-1.0, 2.5, 2.0));
    }

    @Test
    public void testTriangleInside() {
        assertTrue("Точка (0.5, -1.0) внутри треугольника с r=2",
                areaCheck.checkHit(0.5, -1.0, 2.0));
    }

    @Test
    public void testTriangleOutside() {
        assertFalse("X=1.5 > R/2=1  вне треугольника",
                areaCheck.checkHit(1.5, -0.5, 2.0));
        assertFalse("Y=-2.5 < -R=-2  вне треугольника",
                areaCheck.checkHit(0.5, -2.5, 2.0));
        assertFalse("Точка (0.8, -0.5) ниже гипотенузы треугольника",
                areaCheck.checkHit(0.8, -0.5, 2.0));
    }

    @Test
    public void testThirdQuadrantAlwaysMiss() {
        assertFalse("Любая точка в третьем квадранте не попадает: (-1.0, -1.0)",
                areaCheck.checkHit(-1.0, -1.0, 2.0));
    }
}