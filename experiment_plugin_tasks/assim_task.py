"""Forcing task."""
import os
import shutil
from datetime import timedelta
import json
#import logging
import yaml
from netCDF4 import Dataset
import numpy as np
from sfcpert.letkf_exp import run_enkf
from experiment.tasks import AbstractTask


class ExternalAssim(AbstractTask):
    """Perturb state task."""

    def __init__(self, config):
        """Construct assim task.

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
        #mbr = self.config.get_value("general.realization")
        nens = len(self.config.get_value("forecast.ensmsel"))
        archive_dir = self.config.get_value("system.archive_dir")
        first_guess_dir = self.platform.substitute(archive_dir, basetime=self.fg_dtg)
        ana_dir = self.platform.substitute(archive_dir, basetime=self.dtg)
 
        diag_file = self.platform.substitute("SURFOUT.@YYYY@@MM_LL@@DD_LL@_@HH_LL@h00.nc",basetime=self.fg_dtg, validtime=self.dtg)

        obpattern = self.config.get_value("assim.obpath")
        obpattern = self.platform.substitute(obpattern, basetime=self.fg_dtg)
        bgpattern = first_guess_dir + "@mbr@/" + "SURFOUT" + self.suffix
        hofxpattern = first_guess_dir + "@mbr@/" + diag_file
        anpattern = ana_dir + "@mbr@/" + "ANALYSIS" + self.suffix
        cfg_file = self.platform.substitute(self.config.get_value("assim.config"))
        print(bgpattern)
        print(anpattern)
        print(hofxpattern)
        print(obpattern)
        print(cfg_file)
        run_enkf(cfg_file, bgpattern, obpattern, anpattern, hofxpattern, nens)
        
        for i in range(nens):
            fc_start_sfx = self.wrk + "%03d" % i + "/fc_start_sfx"
            os.makedirs(os.path.dirname(fc_start_sfx), exist_ok=True)
            if os.path.islink(fc_start_sfx):
                os.unlink(fc_start_sfx)
            os.symlink(anpattern.replace("@mbr@", "%03d" % i), fc_start_sfx)



