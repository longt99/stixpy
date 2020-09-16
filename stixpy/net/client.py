import astropy.units as u

from astropy.time.core import TimeDelta
from sunpy.net.dataretriever import GenericClient
from sunpy.time import TimeRange
from sunpy.util.scraper import Scraper

__all__ = ["STIXClient"]

BASE_PATTERN = r'http://pub023.cs.technik.fhnw.ch/data/new/' \
               r'{level}/%Y/%m/%d/{type}/solo_{level}_stix-{product}_%Y%m%d_V01\.fits'


class STIXClient(GenericClient):
    """
    Provides access to SolarOrbite STIX data

    Searches data hosted by the `FHNW <http://http://pub023.cs.technik.fhnw.ch/data/>`__.

    Examples
    --------

    """

    def _get_url_for_timerange(self, timerange, **kwargs):
        """
        Returns list of URLS corresponding to value of input timerange.
        Parameters
        ----------
        timerange: `sunpy.time.TimeRange`
            time range for which data is to be downloaded.
        Returns
        -------
        urls : list
            list of URLs corresponding to the requested time range
        """

        # TODO swap over to API once fits files are indexed and API fixed

        level = kwargs.get('level', 1)
        if level != 1:
            raise NotImplementedError(f'Currently only level 1 supported not {level}')

        datatypes = kwargs.get('datatype', ['sci', 'ql'])
        dataproduct = kwargs.get('dataproduct', '.*').replace('_', '-')

        files = []
        for dt in datatypes:
            scraper = Scraper(BASE_PATTERN, level=f'L{level}',
                              type=f'{dt.upper()}', product=dataproduct)
            cur_files = scraper.filelist(timerange)
            files.extend(cur_files)
        return files

    @staticmethod
    def _get_time_for_url(urls):
        """
        Extract time from given urls

        Parameters
        ----------
        urls

        Returns
        -------

        """
        crawler = Scraper(BASE_PATTERN, level='L1', type='QL', product='ql-lightcurve')
        times = list()
        for url in urls:
            t0 = crawler._extractDateURL(url)
            # hard coded full day as that's the normal.
            times.append(TimeRange(t0, t0 + TimeDelta(1*u.day)))
        return times

    def _makeimap(self):
        """
        Helper Function used to hold information about source.
        """
        self.map_['source'] = 'FHNW'
        self.map_['provider'] = 'FHNW'
        self.map_['instrument'] = 'STIX'
        self.map_['physobs'] = 'X-ray'

    @classmethod
    def _can_handle_query(cls, *query):
        """
        Answers whether client can service the query.
        Parameters
        ----------
        query : list of query objects
        Returns
        -------
        boolean
            answer as to whether client can service the query
        """
        # Import here to prevent circular imports
        from sunpy.net import attrs as a

        required = {a.Time, a.Instrument}
        optional = {a.Level, a.stix.DataType, a.stix.DataProduct}
        if not cls.check_attr_types_in_query(query, required, optional):
            return False
        else:
            return True


    @classmethod
    def _attrs_module(cls):
        return 'stix', 'stixpy.net.attrs'
    #
    # @classmethod
    # def register_values(cls):
    #     from sunpy.net import attrs
    #     goes_number = [16, 17]
    #     adict = {attrs.Instrument: [
    #         ("SUVI", "The Geostationary Operational Environmental Satellite Program.")],
    #         attrs.goes.SatelliteNumber: [(str(x), f"GOES Satellite Number {x}") for x in goes_number]}
    #     return adict


    @classmethod
    def register_values(cls):
        from sunpy.net import attrs
        adict = {attrs.Instrument: [('STIX', 'Spectrometer/Telescope for Imaging X-rays')],
                 attrs.Level: [('L0', 'STIX: Binary Telemetry with basic header information.'),
                               ('L1', 'STIX: Decommutated, uncompressed, uncalibrated data.'),
                               ('L2', 'STIX: Calibrated science ready data.')],
                 attrs.stix.DataType: [('QL', 'Quick Look'),
                                       ('SCI', 'Science Data'),
                                       ('HK', 'House Keeping ')],
                 attrs.stix.DataProduct: [('ql_lightcurve', 'Quick look light curve'),
                                          ('ql_background', 'Quick look background light curve'),
                                          ('ql_variance', 'Quick look variance curve'),
                                          ('ql_spectra', 'Quick look spectra'),
                                          ('ql_calibration_spectrum', 'Quick look energy '
                                                                      'calibration spectrum'),
                                          ('ql_flareflag', 'Quick look energy calibration spectrum'),
                                          ('xray_l0', 'Uncompressed pixel counts (12)'),
                                          ('xray_l1', 'Compressed pixel counts (12)'),
                                          ('xray_l2', 'Compressed summed pixel counts (4)'),
                                          ('xray_l3', 'Compressed visibilities'),
                                          ('spectrogram', 'spectrogram')]
                 }
        return adict
