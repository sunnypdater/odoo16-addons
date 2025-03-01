=================================
Thai Localization - Base Sequence
=================================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:83c0f2fc5fecaaa0ea5d1501aaf9575e75f64820b68df5a9066901d97854eb27
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fl10n--thailand-lightgray.png?logo=github
    :target: https://github.com/OCA/l10n-thailand/tree/16.0/l10n_th_base_sequence
    :alt: OCA/l10n-thailand
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/l10n-thailand-16-0/l10n-thailand-16-0-l10n_th_base_sequence
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/l10n-thailand&target_branch=16.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

This module refactor the `ir.sequence` allowing more legends to be added with minimal code duplication and
adding `preview` fields on both `ir.sequence` and `ir.sequence.date_range` models.
the `preview` field is a computed fields that only visible in edit-mode of the form view works with `range_` and `range_end_`.
It helps users to check and validate the prefix, suffix, and padding configuration easily without a need to actually generate an actual document.

Adding more legends to `ir.sequence` requires an extension of an inner method `_interpolation_dict()`
of the `_get_prefix_suffix()` method. An extension of an inner method is impractical,
therefore this module override the `_get_prefix_suffix()` method
by moving the inner private method `_interpolation_dict()` to a private method.
Therefore, this allows another module to add more legends to the `ir.sequence`.

This modules works as a base module to other modules to add more legends to `ir.sequence`.
and extends the `ir.sequence` allowing `range_end_` , `range_period_` and `qoy` legends. It adds the following legends:

* The end of `date_range` year with century: `%(range_end_year)s`
* The end of `date_range` year without century: `%(range_end_y)s`
* The end of `date_range` month: `%(range_end_month)s`
* The end of `date_range` day: `%(range_end_day)s`
* The end of `date_range` day of the year: `%(range_end_doy)s`
* The end of `date_range` week of the year: `%(range_end_woy)s`
* The end of `date_range` weekday: `%(range_end_weekday)s`
* The end of `date_range` hour in 24-hour: `%(range_end_h24)s`
* The end of `date_range` hour in 12-hour: `%(range_end_h12)s`
* The end of `date_range` minute: `%(range_end_min)s`
* The end of `date_range` second: `%(range_end_sec)s`
* The period of `date_range` month: `%(range_period_month)s`
* Quarter of the Year: `%(qoy)s`
* The begin of `date_range` quarter of the Year: `%(range_qoy)s`
* The end of `date_range` quarter of the Year: `%(range_end_qoy)s`
* Current Buddhist Era (BE) year with century: `%(year_be)s`
* Current Buddhist Era (BE) year without century: `%(y_be)s`
* The begin of `date_range` Buddhist Era (BE) year with century: `%(range_year_be)s`
* The begin of `date_range` Buddhist Era (BE) year without century: `%(range_y_be)s`
* The end of `date_range` Buddhist Era (BE) year with century: `%(range_end_year_be)s`
* The end of `date_range` Buddhist Era (BE) year without century: `%(range_end_y_be)s`

**Table of contents**

.. contents::
   :local:

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/l10n-thailand/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/l10n-thailand/issues/new?body=module:%20l10n_th_base_sequence%0Aversion:%2016.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* Sansiri Tanachutiwat
* Ecosoft

Contributors
~~~~~~~~~~~~

* `TGGS KMUTNB <http://tggs.kmtunb.ac.th>`__:

  * Sansiri Tanachutiwat <sansiri.t@tggs.kmutnb.ac.th>

* `Ecosoft <http://ecosoft.co.th>`__:

  * Saran Lim. <saranl@ecosoft.co.th>

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

.. |maintainer-sansirit| image:: https://github.com/sansirit.png?size=40px
    :target: https://github.com/sansirit
    :alt: sansirit
.. |maintainer-Saran440| image:: https://github.com/Saran440.png?size=40px
    :target: https://github.com/Saran440
    :alt: Saran440

Current `maintainers <https://odoo-community.org/page/maintainer-role>`__:

|maintainer-sansirit| |maintainer-Saran440| 

This module is part of the `OCA/l10n-thailand <https://github.com/OCA/l10n-thailand/tree/16.0/l10n_th_base_sequence>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
