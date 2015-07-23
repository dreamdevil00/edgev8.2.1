##
# Portions Copyright (c) Microsoft Corporation. All rights reserved. 
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0  
#
# THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION 
# ANY IMPLIED WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR 
# PURPOSE, MERCHANTABLITY OR NON-INFRINGEMENT. 
#
# See the Apache Version 2.0 License for specific language governing 
# permissions and limitations under the License.
##
{
  'targets': [
    {
      'target_name': 'install_coreclr',
      'type': 'none',
      'conditions': [
        [
          'OS!="win"',
          {
            'variables': {
              'dnx_root': '<!(readlink -m "$(which dnx)/../../../../")'
            },
            'actions': [
	          {
	            'action_name': 'install_mono_clr',
	            'inputs': [],
	            'outputs': ['<(dnx_root)/runtimes/dnx-mono-linux-x64.1.0.0-beta7-12255/bin/libcoreclr.so'],
	            'action': [
	              'bash',
	              '-c',
	              'source <(dnx_root)/dnvm/dnvm.sh && dnvm install 1.0.0-beta7-12255 -r mono -u && chmod 755 <(dnx_root)/runtimes/dnx-mono-linux-x64.1.0.0-beta7-12255/bin/dnu',
	            ]
	          },
	          {
	            'action_name': 'install_coreclr',
	            'inputs': [],
	            'outputs': ['<(dnx_root)/runtimes/dnx-coreclr-linux-x64.1.0.0-beta7-12255/bin/libcoreclr.so'],
	            'action': [
	              'bash',
	              '-c',
	              'source <(dnx_root)/dnvm/dnvm.sh && dnvm install 1.0.0-beta7-12255 -r coreclr -u && chmod 755 <(dnx_root)/runtimes/dnx-coreclr-linux-x64.1.0.0-beta7-12255/bin/dnu',
	            ]
	          }
	        ]
          }
        ]
      ]
    },
    {
      'target_name': 'edge',
      'dependencies': [
        'install_coreclr'
      ],
      'include_dirs': [
        "<!(node -e \"require('nan')\")"
      ],
      'sources': [
        'src/common/v8synchronizationcontext.cpp'
      ],
      'conditions': [
        [
          'OS=="win"',
          {
            'sources+': [
              'src/dotnet/edge.cpp',
              'src/dotnet/utils.cpp',
              'src/dotnet/clrfunc.cpp',
              'src/dotnet/clrfuncinvokecontext.cpp',
              'src/dotnet/nodejsfunc.cpp',
              'src/dotnet/nodejsfuncinvokecontext.cpp',
              'src/dotnet/persistentdisposecontext.cpp',
              'src/dotnet/clrfuncreflectionwrap.cpp',
              'src/dotnet/clractioncontext.cpp'
            ]
          },
          {
            'sources+': [
              'src/common/edge.cpp'
            ],
            'cflags+': [
              '-std=c++11'
            ],
            'conditions': [
              [
                '"<!(echo -n `which dnx`)"!=""',
                {
                  'cflags+': [
                    '-DHAVE_CORECLR'
                  ],
                  'sources+': [
                    'src/coreclr/coreclrembedding.cpp',
                    'src/coreclr/coreclrfunc.cpp',
                    'src/coreclr/coreclrnodejsfunc.cpp',
                    'src/coreclr/coreclrfuncinvokecontext.cpp',
                    'src/coreclr/coreclrnodejsfuncinvokecontext.cpp',
                    'src/common/utils.cpp'
                  ]
                }
              ],
              [
                '"<!(echo -n `which mono`)"!=""',
                {
                  'sources+': [
                    'src/mono/clractioncontext.cpp',
                    'src/mono/clrfunc.cpp',
                    'src/mono/clrfuncinvokecontext.cpp',
                    'src/mono/monoembedding.cpp',
                    'src/mono/task.cpp',
                    'src/mono/dictionary.cpp',
                    'src/mono/nodejsfunc.cpp',
                    'src/mono/nodejsfuncinvokecontext.cpp',
                    'src/mono/utils.cpp',
                    'src/common/utils.cpp'
                  ],
                  'include_dirs': [
                    '<!@(pkg-config mono-2 --cflags-only-I | sed s/-I//g)'
                  ],
                  'link_settings': {
                    'libraries': [
                      '<!@(pkg-config mono-2 --libs)'
                    ],

                  },
                  'cflags+': [
                    '-DHAVE_MONO'
                  ]
                }
              ]
            ]
          }
        ]
      ],
      'configurations': {
        'Release': {
          'msvs_settings': {
            'VCCLCompilerTool': {
              # this is out of range and will generate a warning and skip adding RuntimeLibrary property:
              'RuntimeLibrary': -1,
              # this is out of range and will generate a warning and skip adding RuntimeTypeInfo property:
              'RuntimeTypeInfo': -1,
              'BasicRuntimeChecks': -1,
              'ExceptionHandling': '0',
              'AdditionalOptions': [
                '/clr',
                '/wd4506'
              ]
            },
            'VCLinkerTool': {
              'AdditionalOptions': [
                '/ignore:4248'
              ]
            }
          }
        },
        'Debug': {
          'msvs_settings': {
            'VCCLCompilerTool': {
              # this is out of range and will generate a warning and skip adding RuntimeLibrary property:
              'RuntimeLibrary': -1,
              # this is out of range and will generate a warning and skip adding RuntimeTypeInfo property:
              'RuntimeTypeInfo': -1,
              'BasicRuntimeChecks': -1,
              'ExceptionHandling': '0',
              'AdditionalOptions': [
                '/clr',
                '/wd4506'
              ]
            },
            'VCLinkerTool': {
              'AdditionalOptions': [
                '/ignore:4248'
              ]
            }
          }
        }
      }
    },
    {
      'target_name': 'build_managed',
      'conditions': [
        [
          'OS!="win"',
          {
            'type': 'none',
            'dependencies': [
              'edge'
            ],
            'conditions': [
              [
                '"<!(echo -n `which mono`)"!=""',
                {
                  'actions+': [
                    {
                      'action_name': 'compile_mono_embed',
                      'inputs': [
                        'src/mono/*.cs'
                      ],
                      'outputs': [
                        'src/mono/monoembedding.exe'
                      ],
                      'action': [
                        'dmcs',
                        '-sdk:4.5',
                        '-target:exe',
                        '-out:build/$(BUILDTYPE)/MonoEmbedding.exe',
                        'src/mono/*.cs',
                        'src/common/*.cs'
                      ]
                    }
                  ]
                }
              ],
              [
                '"<!(echo -n `which dnx`)"!=""',
                {
                  'actions+': [
                    {
                      'action_name': 'restore_packages',
                      'inputs': [],
                      'outputs': [
                        'src/coreclr/packages/'
                      ],
                      'action': [
                        'bash',
                        '-c',
                        'cd src/coreclr && <(dnx_root)/runtimes/dnx-mono-linux-x64.1.0.0-beta7-12255/bin/dnu restore'
                      ]
                    },
                    {
                      'action_name': 'compile_coreclr_embed',
                      'inputs': [
                        'src/coreclr/*.cs'
                      ],
                      'outputs': [
                        'build/$(BUILDTYPE)/CoreCLREmbedding.dll'
                      ],
                      'action': [
                        'mcs',
                        '/nostdlib',
                        '/noconfig',
                        '/unsafe',
                        '/r:<!(dirname `which dnx`)/System.Console.dll',
                        '/r:<!(dirname `which dnx`)/System.Runtime.dll',
                        '/r:<!(dirname `which dnx`)/System.Dynamic.Runtime.dll',
                        '/r:<!(dirname `which dnx`)/System.ObjectModel.dll',
                        '/r:<!(dirname `which dnx`)/System.Private.Uri.dll',
                        '/r:<!(dirname `which dnx`)/System.IO.FileSystem.dll',
                        '/r:<!(dirname `which dnx`)/System.Linq.dll',
                        '/r:<!(dirname `which dnx`)/System.Linq.Expressions.dll',
                        '/r:<!(dirname `which dnx`)/System.Reflection.dll',
                        '/r:<!(dirname `which dnx`)/mscorlib.dll',
                        '-sdk:4.5',
                        '-target:library',
                        '-out:build/$(BUILDTYPE)/CoreCLREmbedding.dll',
                        'src/coreclr/*.cs',
                        'src/common/*.cs'
                      ]
                    }
                  ]
                }
              ]
            ]
          }
        ]
      ]
    }
  ]
}
