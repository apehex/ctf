for i in {0000..9999}; do
    echo "UoMYTrfrBFHyQXmg6gzctqAwOmw1IohZ $i" >> pins;
done

cat pins | nc -w 1 localhost 30002
