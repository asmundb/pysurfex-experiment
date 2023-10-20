"""Forcing task."""
import os
import shutil
from datetime import timedelta
import json
#import logging
import yaml
from netCDF4 import Dataset
import numpy as np
from sfcpert.perturb_state import perturb_state
from experiment.tasks import AbstractTask


class PerturbState(AbstractTask):
    """Perturb state task."""

    def __init__(self, config):
        """Construct perturb state task.

        Args:
            config (dict): Actual configuration dict

        """
        AbstractTask.__init__(self, config, name="PerturbState")
        self.var_name = self.config.get_value("task.var_name")
        try:
            user_config = self.config.get_value("task.forcing_user_config")
        except AttributeError:
            user_config = None
        self.user_config = user_config

    def execute(self):
        """Execute the perturb state task.

        Raises:
            NotImplementedError: _description_
        """
        dtg = self.dtg
        fcint = self.fcint

        kwargs = {}
        if self.user_config is not None:
            user_config = yaml.safe_load(open(self.user_config, mode="r", encoding="utf-8"))
            kwargs.update({"user_config": user_config})

        with open(self.wdir + "/domain.json", mode="w", encoding="utf-8") as file_handler:
            json.dump(self.geo.json, file_handler, indent=2)
        kwargs.update({"domain": self.wdir + "/domain.json"})
        
        kwargs.update({"dtg_start": dtg.strftime("%Y%m%d%H")})
        kwargs.update({"dtg_stop": (dtg + fcint).strftime("%Y%m%d%H")})
        mbr = self.config.get_value("general.realization")
        #noise_cfg = self.platform.substitute(self.config.get_value("eps.config"))
        archive_dir = self.config.get_value("system.archive_dir")
        first_guess_dir = self.platform.substitute(archive_dir, basetime=self.fg_dtg)
        #input_forcing_dir = forcing_dir[:-4]

        #noise_file = forcing_dir + "noise_%03d.nc" % int(mbr)
        output_format = self.config.get_value("SURFEX.IO.CFORCING_FILETYPE").lower()
        variables = ["WSN_VEG", "HSN_VEG", "RSN_VEG", "SAG_VEG"]
        nsnowlayers = 12
        all_vars = []
        for var in variables:
            for il in range(nsnowlayers):
                all_vars += [f"{var}{il+1}"]
        cfg = {"nens": 10,
               "corrlen": 3,
               "std": 0.5,
               "alpha": 0}
     
        print("vars",all_vars)
        print("filename", self.fc_start_sfx)
        print(cfg)
        perturb_state(all_vars, self.fc_start_sfx, cfg)
        #input_forcing_file = input_forcing_dir + "/FORCING.nc"
        #if output_format == "netcdf":
        #    output = first_guess_dir + "/.nc"
        #else:
        #    raise NotImplementedError(output_format)

        #kwargs.update({"of": output})
        #kwargs.update({"output_format": output_format})

        #pattern = self.config.get_value("forcing.pattern")
        #input_format = self.config.get_value("forcing.input_format")
        #kwargs.update({"geo_input_file": self.config.get_value("forcing.input_geo_file")})
        #timestep = self.config.get_value("forcing.timestep")
        #debug = self.config.get_value("forcing.debug")

        #kwargs.update({"input_format": input_format})
        #kwargs.update({"pattern": pattern})
        #kwargs.update({"debug": debug})
        #kwargs.update({"timestep": timestep})

        #with open(noise_cfg) as f:
        #    cfg = json.load(f)

        #
        #print("call perturb atm forcing for mbr %s" % mbr)
        #perturb_forcing(input_forcing_file, noise_file, output, cfg)



