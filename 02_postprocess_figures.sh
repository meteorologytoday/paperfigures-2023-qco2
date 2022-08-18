#!/bin/bash


echo "Making output directory 'final_figures'..."
mkdir final_figures


echo "Making final figures... "


# Merging two sub-figures
convert \( figures/ocean_SST.png \) \
    \( figures/seaice_vol.png \) -gravity center +append \
     figures/merged-global-diag.png

convert \( figures/AMOC_POP2.png \) \
    \( figures/AMOC_psi.png -scale 60% \) -gravity center -append \
     figures/merged-AMOC.png

convert \( figures/diff_zmean_PAC.png -rotate 90 -gravity North -background white -splice 0x250 -gravity North -pointsize 120 -annotate +0+150 '(a) PAC' -rotate -90 \) \
        \( figures/diff_zmean_ATL.png -rotate 90 -gravity North -background white -splice 0x250 -gravity North -pointsize 120 -annotate +0+150 '(b) ATL' -rotate -90 \) \
        \( figures/diff_zmean_IND.png -rotate 90 -gravity North -background white -splice 0x250 -gravity North -pointsize 120 -annotate +0+150 '(c) IND' -rotate -90 \) \
     -append \
     figures/merged-diff_zmean.png


convert \( figures/diff_zmean_ln_PAC.png -gravity North -background white -splice 0x200 -gravity North -pointsize 120 -annotate +200+150 '(a) PAC' \) \
        \( figures/diff_zmean_ln_ATL.png -gravity North -background white -splice 0x200 -gravity North -pointsize 120 -annotate +200+150 '(b) ATL' \) \
        \( figures/diff_zmean_ln_IND.png -gravity North -background white -splice 0x200 -gravity North -pointsize 120 -annotate +200+150 '(c) IND' \) \
     +append \
     figures/merged-diff_zmean_ln.png






name_pairs=(
    merged-global-diag.png          fig01.png
    merged-AMOC.png                 fig02.png
    diff_map_SST-PREC_TOTAL.png     fig03.png
    merged-diff_zmean.png           fig04.png
    merged-diff_zmean_ln.png        fig05.png
)

N=$(( ${#name_pairs[@]} / 2 ))
echo "We have $N figure(s) to rename."
for i in $( seq 1 $N ) ; do
    src_file="${name_pairs[$(( (i-1) * 2 + 0 ))]}"
    dst_file="${name_pairs[$(( (i-1) * 2 + 1 ))]}"
    echo "$src_file => $dst_file"
    cp figures/$src_file final_figures/$dst_file 
done

echo "Done."
