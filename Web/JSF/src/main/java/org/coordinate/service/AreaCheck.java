    //
    // Source code recreated from a .class file by IntelliJ IDEA
    // (powered by FernFlower decompiler)
    //
//
//    package org.coordinate.service;
//
//    import jakarta.enterprise.context.ApplicationScoped;
//    import jakarta.inject.Named;
//    import java.io.Serializable;
//
//
//
//
//    @Named("areaCheckService")
//    @ApplicationScoped
//    public class AreaCheck implements Serializable {
//
//
//
//        public boolean checkHit(double x, double y, double r) {
//            if (x >= (double)0.0F && y >= (double)0.0F) {
//                return x * x + y * y <= r * r;
//            } else if (x <= (double)0.0F && y >= (double)0.0F) {
//                return x > -r && y <= r;
//            } else if (x >= (double)0.0F && y <= (double)0.0F) {
//                return x <= r / (double)2.0F && y >= -r && y >= (double)2.0F * x - r;
//            } else {
//                return false;
//            }
//        }
//    }

//    package org.coordinate.service;
//
//    import jakarta.enterprise.context.ApplicationScoped;
//    import jakarta.inject.Named;
//    import java.io.Serializable;
//
//    @Named("areaCheckService")
//    @ApplicationScoped
//    public class AreaCheck implements Serializable {
//
//        public boolean checkHit(double x, double y, double r) {
//            try {
//                Thread.sleep(200);
//            } catch (InterruptedException e) {
//                Thread.currentThread().interrupt();
//            }
//
//            if (x >= (double)0.0F && y >= (double)0.0F) {
//                return x * x + y * y <= r * r;
//            } else if (x <= (double)0.0F && y >= (double)0.0F) {
//                return x > -r && y <= r;
//            } else if (x >= (double)0.0F && y <= (double)0.0F) {
//                return x <= r / (double)2.0F && y >= -r && y >= (double)2.0F * x - r;
//            } else {
//                return false;
//            }
//        }
//    }



    package org.coordinate.service;

    import jakarta.enterprise.context.ApplicationScoped;
    import jakarta.inject.Named;
    import java.io.Serializable;

    @Named("areaCheckService")
    @ApplicationScoped
    public class AreaCheck implements Serializable {

        public boolean checkHit(double x, double y, double r) {
            long uselessResult = 0;
            for (int i = 0; i < 5000000; i++) {
                uselessResult += Math.sqrt(x * x + y * y) * Math.sin(i) * Math.cos(i);
            }

            if (x >= (double)0.0F && y >= (double)0.0F) {
                return x * x + y * y <= r * r;
            } else if (x <= (double)0.0F && y >= (double)0.0F) {
                return x > -r && y <= r;
            } else if (x >= (double)0.0F && y <= (double)0.0F) {
                return x <= r / (double)2.0F && y >= -r && y >= (double)2.0F * x - r;
            } else {
                return false;
            }
        }
    }