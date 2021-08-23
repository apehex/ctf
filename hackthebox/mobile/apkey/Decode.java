import java.util.ArrayList;
import java.lang.StringBuilder;

public class Decode {

    public static void main(String[] args){
        // ciphertext
        char c1 = Decode.ha().charAt(0);
        char c2 = Decode.aa().charAt(8);
        char c3 = Decode.ea().charAt(5);
        char c4 = Decode.ia().charAt(4);
        char c5 = Decode.ha().charAt(1);
        char c6 = Decode.ha().charAt(4);
        char c7 = Decode.ha().charAt(3);
        char c8 = Decode.ha().charAt(3);
        char c9 = Decode.ha().charAt(0);
        char c10 = Decode.aa().charAt(8);
        char c11 = Decode.aa().charAt(8);
        char c12 = Decode.ia().charAt(0);
        char c13 = Decode.ca().charAt(3);
        char c14 = Decode.fa().charAt(3);
        char c15 = Decode.fa().charAt(0);
        char c16 = Decode.ca().charAt(0);

        StringBuilder key = new StringBuilder();
        key.append(String.valueOf(c1));
        key.append(String.valueOf(c2));
        key.append(String.valueOf(c3));
        key.append(String.valueOf(c4));
        key.append(String.valueOf(c5).toLowerCase());
        key.append(String.valueOf(c6));
        key.append(String.valueOf(c7).toLowerCase());
        key.append(String.valueOf(c8));
        key.append(String.valueOf(c9));
        key.append(String.valueOf(c10).toLowerCase());
        key.append(String.valueOf(c11).toLowerCase());
        key.append(String.valueOf(c12));
        key.append(String.valueOf(c13).toLowerCase());
        key.append(String.valueOf(c14));
        key.append(String.valueOf(c15));
        key.append(String.valueOf(c16));

        // algorithm
        c1 = Decode.da().charAt(1);
        c2 = Decode.ia().charAt(2);
        c3 = Decode.ia().charAt(1);

        StringBuilder algorithm = new StringBuilder();
        algorithm.append(String.valueOf(c1));
        algorithm.append(String.valueOf(c2));
        algorithm.append(String.valueOf(c3));

        System.out.println(key.toString());
        System.out.println(algorithm.toString());
        System.out.println(Decode.ga());
    }

    public static String ha() {
        ArrayList<String> arrayList = new ArrayList();
        arrayList.add("8GGfdt");
        arrayList.add("7654rF");
        arrayList.add("09Hy24");
        arrayList.add("56Gth6");
        arrayList.add("hdgKj8");
        arrayList.add("kdIdu8");
        arrayList.add("kHtZuV");
        arrayList.add("jHurf6");
        arrayList.add("5tgfYt");
        arrayList.add("kd9Iuy");
        return arrayList.get(6);
    }

    public static String aa() {
        ArrayList<String> arrayList = new ArrayList();
        arrayList.add("LmBf5G6h9j");
        arrayList.add("3De3f4HbnK");
        arrayList.add("hdKD7b87yb");
        arrayList.add("85S94kFpV1");
        arrayList.add("dCV4f5G90h");
        arrayList.add("34Jnf8ku4F");
        arrayList.add("ld7HV5F4d2");
        arrayList.add("el0oY7gF54");
        arrayList.add("lsKJt69jo8");
        arrayList.add("Kju87F5dhk");
        return arrayList.get(3);
    }

    public static String ea() {
        ArrayList<String> arrayList = new ArrayList();
        arrayList.add("TG7ygj");
        arrayList.add("U8uu8i");
        arrayList.add("gGtT56");
        arrayList.add("84hYDG");
        arrayList.add("ejhHy6");
        arrayList.add("7ytr4E");
        arrayList.add("j5jU87");
        arrayList.add("HyeaX9");
        arrayList.add("jd9Idu");
        arrayList.add("kd546G");
        return arrayList.get(7);
    }

    public static String ia() {
        ArrayList<String> arrayList = new ArrayList();
        arrayList.add("9GDFt6");
        arrayList.add("83h736");
        arrayList.add("kdiJ78");
        arrayList.add("vcbGT6");
        arrayList.add("rSE6qY");
        arrayList.add("kFgde4");
        arrayList.add("5drDr4");
        arrayList.add("Y6ttr5");
        arrayList.add("444w45");
        arrayList.add("hjKd56");
        return arrayList.get(4);
    }

    public static String ca() {
        ArrayList<String> arrayList = new ArrayList();
        arrayList.add("5d5d6Y");
        arrayList.add("g7Fr3d");
        arrayList.add("44r5T5");
        arrayList.add("Hg6t89");
        arrayList.add("FlEGyL");
        arrayList.add("8iIi89");
        arrayList.add("uiu445g");
        arrayList.add("JJgF55");
        arrayList.add("lhjko0");
        arrayList.add("t53rfs");
        return arrayList.get(4);
    }

    public static String fa() {
        ArrayList<String> arrayList = new ArrayList();
        arrayList.add("JuFtt5");
        arrayList.add("6HxWkw");
        arrayList.add("ojG4es");
        arrayList.add("yhngR4");
        arrayList.add("fFdsEe");
        arrayList.add("8878yu");
        arrayList.add("h6h6y7");
        arrayList.add("juJ8i9");
        arrayList.add("sfrt46");
        arrayList.add("ksid80");
        return arrayList.get(1);
    }

    public static String da() {
        ArrayList<String> arrayList = new ArrayList();
        arrayList.add("wAxcoc");
        arrayList.add("j48duH");
        arrayList.add("kJDH78");
        arrayList.add("748HDj");
        arrayList.add("jDKDO9");
        arrayList.add("UJuiu8");
        arrayList.add("637g73");
        arrayList.add("kd0o0d");
        arrayList.add("l3K39I");
        arrayList.add("lSPgt6");
        return arrayList.get(0);
    }

    public static String ga() {
        StringBuilder stringBuilder = new StringBuilder();
        ArrayList<String> arrayList = new ArrayList();
        arrayList.add("722gFc");
        arrayList.add("n778Hk");
        arrayList.add("jvC5bH");
        arrayList.add("lSu6G6");
        arrayList.add("HG36Hj");
        arrayList.add("97y43E");
        arrayList.add("kjHf5d");
        arrayList.add("85tR5d");
        arrayList.add("1UlBm2");
        arrayList.add("kI94fD");
        stringBuilder.append(arrayList.get(8));
        stringBuilder.append(Decode.ha());
        stringBuilder.append(Decode.ia());
        stringBuilder.append(Decode.fa());
        stringBuilder.append(Decode.ea());
        arrayList = new ArrayList<String>();
        arrayList.add("ue7888");
        arrayList.add("6HxWkw");
        arrayList.add("gGhy77");
        arrayList.add("837gtG");
        arrayList.add("HyTg67");
        arrayList.add("GHR673");
        arrayList.add("ftr56r");
        arrayList.add("kikoi9");
        arrayList.add("kdoO0o");
        arrayList.add("2DabnR");
        stringBuilder.append(arrayList.get(9));
        stringBuilder.append(Decode.ca());
        arrayList = new ArrayList<String>();
        arrayList.add("jH67k8");
        arrayList.add("8Huk89");
        arrayList.add("fr5GtE");
        arrayList.add("Hg5f6Y");
        arrayList.add("o0J8G5");
        arrayList.add("Wod2bk");
        arrayList.add("Yuu7Y5");
        arrayList.add("kI9ko0");
        arrayList.add("dS4Er5");
        arrayList.add("h93Fr5");
        stringBuilder.append(arrayList.get(5));
        stringBuilder.append(Decode.da());
        stringBuilder.append(Decode.aa());
        return stringBuilder.toString();
    }
}
