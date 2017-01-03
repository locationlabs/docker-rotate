Version 3.2:
 - Added compatibility for pre-1.21 API for use with a pre-1.9 engine.

Version 3.1:
 - Changed image deletion to use tags, not Ids. This fixes an issue when deleting an image
   that is a parent of another image.

Version 3.0:
 - reworked API, again - this version is a lot clearer and more explicit about what it does
 - fixed issues around images with multiple names
 - added limited unit tests
 - added integration tests

Version 2.0.1:
 - Changed owner of travis CI job

Version 2.0:
 - updated command line API - container and images modes are now separate
 - better control of container cleanup

Version 1.2:
 - Fix missing package definition

Version 1.1:
 - Ensure that project name matches directory structure.
 - Better handling of container deletion errors.

Version 1.0:
 - Initial release
