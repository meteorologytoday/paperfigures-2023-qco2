#!/bin/bash

py=python3
jl=julia
bs=bash
srcdir=src

plot_codes=(
    $jl $srcdir/plot_AMOC.jl
    $py $srcdir/plot_AMOC_psi.py
    $jl $srcdir/plot_seaice.jl
    $jl $srcdir/plot_SST.jl
    $py $srcdir/plot_diff_map_SST_PREC.py
    $py "$srcdir/plot_diff_zmean_vertical.py --region=PAC"
    $py "$srcdir/plot_diff_zmean_vertical.py --region=ATL"
    $py "$srcdir/plot_diff_zmean_vertical.py --region=IND"
    $py "$srcdir/plot_diff_zmean_ln.py --region=PAC"
    $py "$srcdir/plot_diff_zmean_ln.py --region=ATL --thumbnail-skip 4"
    $py "$srcdir/plot_diff_zmean_ln.py --region=IND --thumbnail-skip 4"
    $py "$srcdir/plot_OHT_decomposition.py --region=PAC --thumbnail-skip 3"
    $py "$srcdir/plot_OHT_decomposition.py --region=ATL --thumbnail-skip 7"
    $py "$srcdir/plot_OHT_decomposition.py --region=IND --thumbnail-skip 7"
)


# Some code to download data and extract them


mkdir figures

N=$(( ${#plot_codes[@]} / 2 ))
echo "We have $N file(s) to run..."
for i in $( seq 1 $(( ${#plot_codes[@]} / 2 )) ) ; do
    PROG="${plot_codes[$(( (i-1) * 2 + 0 ))]}"
    FILE="${plot_codes[$(( (i-1) * 2 + 1 ))]}"
    echo "=====[ Running file: $FILE ]====="
    eval "$PROG $FILE" &
done


wait

echo "Figures generation is complete."
echo "Please run 02_postprocess_figures.sh to postprocess the figures."
