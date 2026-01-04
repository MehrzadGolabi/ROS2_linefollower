# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_linebot_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED linebot_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(linebot_FOUND FALSE)
  elseif(NOT linebot_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(linebot_FOUND FALSE)
  endif()
  return()
endif()
set(_linebot_CONFIG_INCLUDED TRUE)

# output package information
if(NOT linebot_FIND_QUIETLY)
  message(STATUS "Found linebot: 1.0.0 (${linebot_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'linebot' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT linebot_DEPRECATED_QUIET)
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(linebot_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${linebot_DIR}/${_extra}")
endforeach()
