#!/bin/bash


echo "Making output directory 'final_figures'..."
mkdir final_figures


echo "Making final figures... "


# Merging two sub-figures
convert \( figures/ocean_SST.png \) \
    \( figures/seaice_vol.png \) -gravity center +append \
     figures/merged-global-diag.png

convert \( figures/AMOC_POP2.png \) \
    \( figures/AMOC_psi.png -scale 50% \) -gravity center +append \
     figures/merged-AMOC.png

convert \( figures/merged-global-diag.png \) \
    \( figures/merged-AMOC.png \) -gravity center -append \
     figures/merged-equilibrium-diag.png

#convert \( figures/diff_zmean_vertical_ATL.png -gravity North -background white -splice 0x250 -gravity North -pointsize 120 -annotate +0+150 'ATL' \) \
#        \( figures/diff_zmean_vertical_IND.png -gravity North -background white -splice 0x250 -gravity North -pointsize 120 -annotate +0+150 'IND' \) \
#     +append \
#     figures/merged-diff_zmean.png


for region in PAC ATL IND ; do

    convert \( figures/diff_zmean_ln_$region.png -gravity East -background white -splice 200x0 \) \
            figures/OHT_decomp_$region.png \
         +append \
         figures/diff_zmean_ln_merged-$region.png

    convert figures/diff_zmean_vertical_$region.png \
            \( -resize 44% figures/diff_zmean_ln_merged-$region.png \) \
            +append \
            figures/all-merged-$region.png

done

if [ ] ; then
convert figures/diff_zmean_ln_merged-ATL.png \
        figures/diff_zmean_ln_merged-IND.png \
     +append \
     figures/diff_zmean_ln_merged-ATL-IND.png

convert figures/diff_zmean_vertical_ATL.png \
        figures/diff_zmean_vertical_IND.png \
     +append \
     figures/merged-diff_zmean_vertical-ATL-IND.png
fi


#    merged-global-diag.png          fig01.png
#    merged-AMOC.png                 fig02.png
name_pairs=(
    merged-equilibrium-diag.png             fig01.png
    diff_map_SST-PREC_TOTAL.png             fig02.png
    diff_zmean_vertical_PAC.png             fig03.png
    diff_zmean_ln_merged-PAC.png            fig04.png
    all-merged-ATL.png                      figs01.png
    all-merged-IND.png                      figs02.png
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
