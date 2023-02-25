include("../CESM-diagnostic/src/misc/RunCommands.jl")

using .RunCommands
using Formatting

include("setup.jl")


gonna_do = keys(cases)
atm_varlist = join(["U", "V", "T", "OMEGA", "DTCOND", "TAUX", "TAUY", "PRECL", "PRECC", "Q", "Z3"], ",")
ocn_varlist = join(["TEMP", "SALT", "UVEL", "VVEL", "WVEL", "HMXL"], ",")

ocn_atm_file = joinpath(".", "CESM_domains", "remap_files", "map_gx1v6_TO_fv0.9x1.25_blin.130322.nc") 

for (casename, caseinfo) in cases

    if ! ( casename in gonna_do )
        println("Not gonna do $casename.")
        continue
    end

    println("Doing casename: $casename")
    yrng = caseinfo["yrng"]
    println("Doing year range: $(yrng[1]) to $(yrng[2]). ")

    output_dir_case = format("$output_dir/$casename/{:04d}-{:04d}", yrng[1], yrng[2])

    println("Making path: ", output_dir_case)
    mkpath(output_dir_case)

    atm_data_path = "$archive_root/$casename/atm/hist"
    ocn_data_path = "$archive_root/$casename/ocn/hist"
   
    if caseinfo["model"] == "POP2"
        middle_part = "pop.h"
        Nx_varname = "nlon"
        Ny_varname = "nlat"
    else
        middle_part = "EMOM.h0.mon"
        Nx_varname = "Nx"
        Ny_varname = "Ny"
    end

    file_cmd_pairs = []

    function getCmd_atm(m::Integer)
        atm_input_file  = format("$atm_data_path/$casename.cam.h0.{{{:04d}..{:04d}}}-{:02d}.nc", yrng[1], yrng[2], m)
        atm_output_file = format("$output_dir_case/atm.{:02d}.nc", m)
        cmd = `bash -c "ncra -O -v $(atm_varlist) $atm_input_file $atm_output_file"`

        return (atm_output_file, cmd)
    end

    function getCmd_atm_MSE(m::Integer)
        atm_input_file = format("$output_dir_case/atm.{:02d}.nc", m)
        atm_output_file = format("$output_dir_case/atm.postprocess.{:02d}.nc", m)
        cmd = `bash -c "ncap2 -O -s 'MSE = 1.00464e3 * T + 2.501e6 * Q + 9.80616 * Z3;' $atm_input_file $atm_output_file"`

        return (atm_output_file, cmd)
    end

 
    function getCmd_ocn(m::Integer)
        ocn_input_file  = format("$ocn_data_path/$casename.$middle_part.{{{:04d}..{:04d}}}-{:02d}.nc", yrng[1], yrng[2], m)
        ocn_output_file = format("$output_dir_case/ocn.{:02d}.nc", m)
        cmd = `bash -c "ncra -O -v $(ocn_varlist) $ocn_input_file $ocn_output_file"`

        return (ocn_output_file, cmd)
    end

    function getCmd_ocn_regrid(m::Integer)
        ocn_input_file = format("$output_dir_case/ocn.{:02d}.nc", m)
        ocn_tmp_file = format("$output_dir_case/ocn.{:02d}.nc.tmp", m)
        ocn_output_file = format("$output_dir_case/ocn_regrid.{:02d}.nc", m)

        cmds = []

        if caseinfo["model"] == "POP2"
            ocn_tmp_file = ocn_input_file
        else
            push!(cmds, `ncap2 -O -s "VVEL_T=array(0.0,0.0,/\$time,\$Nz,\$Ny,\$Nx/); VVEL_T=(VVEL(:,:,0:-2,:)+VVEL(:,:,1:,:))/2;" $ocn_input_file $ocn_tmp_file`)
        end 
        push!(cmds, `bash -c "ncremap --no_stdin -m $ocn_atm_file -R '--rgr lon_nm_in=$Nx_varname --rgr lat_nm_in=$Ny_varname' $ocn_tmp_file $ocn_output_file"`)

        if caseinfo["model"] != "POP2"
            push!(cmds, `rm $ocn_tmp_file`)
        end
        return (ocn_output_file, cmds)

    end

    function getCmd_ocn_am()
        input_file  = "$output_dir_case/ocn_regrid.{01..12}.nc"
        output_file = "$output_dir_case/ocn_regrid.am.nc"
        cmd = `bash -c "ncra -O $input_file $output_file"`

        return (output_file, cmd)
    end

    function getCmd_atm_am()
        input_file  = "$output_dir_case/atm.postprocess.{01..12}.nc"
        output_file = "$output_dir_case/atm.am.nc"
        cmd = `bash -c "ncra -O $input_file $output_file"`

        return (output_file, cmd)
    end




    # Making monthly
    for m = 1:12
        push!(file_cmd_pairs, getCmd_atm(m))
        push!(file_cmd_pairs, getCmd_atm_MSE(m))
    end
        
    # Making annual mean
    push!(file_cmd_pairs, getCmd_atm_am())

    # Making monthly
    for m = 1:12
        push!(file_cmd_pairs, getCmd_ocn(m))
        push!(file_cmd_pairs, getCmd_ocn_regrid(m))
    end
        
    # Making annual mean
    push!(file_cmd_pairs, getCmd_ocn_am())
    


    for (output_file, cmd) in file_cmd_pairs
        if isfile(output_file)
            println("File `$output_file` exists. Skip this.")
        else
            pleaseRun(cmd)
        end
    end
        
end

println("Done.")
