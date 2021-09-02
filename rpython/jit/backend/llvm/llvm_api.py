from rpython.rtyper.lltypesystem import rffi, lltype
from rpython.translator.tool.cbuild import ExternalCompilationInfo
from rpython.rtyper.lltypesystem.rffi import str2constcharp, constcharp2str
from pypy import pypydir
import os

class LLVMAPI:
    def __init__(self, debug=False):
        self.debug = debug #disable in prod to prevent castings and comparisons of returned values
        self.define_types()
        self.initialise_api()

    def define_types(self):
        """
        LLVM uses polymorphic types which C can't represent,
        so LLVM-C doesn't define them with concrete/primitive types.
        As such most LLVM types are just void pointers.
        """
        self.Void = lltype.Void
        self.VoidPtr = rffi.VOIDP
        self.VoidPtrPtr = rffi.VOIDPP
        self.ModuleRef = self.VoidPtr
        self.TypeRef = self.VoidPtr
        self.TypeRefPtr = self.VoidPtrPtr
        self.ContextRef = self.VoidPtr
        self.ValueRef = self.VoidPtr
        self.ValueRefPtr = self.VoidPtrPtr
        self.GenericValueRef = self.VoidPtr
        self.BasicBlockRef = self.VoidPtr
        self.BasicBlockRefPtr = self.VoidPtrPtr
        self.BuilderRef = self.VoidPtr
        self.TargetDataRef = self.VoidPtr
        self.Enum = lltype.Signed
        self.Bool = rffi.INT #LLVMBOOL is typedefed to i32
        self.Str = rffi.CONST_CCHARP
        self.VerifierFailureAction = self.Enum
        self.RealPredicate = self.Enum
        self.IntPredicate = self.Enum
        self.TargetDataRef = self.VoidPtr
        self.JITDylibRef = self.VoidPtr
        self.ThreadSafeModuleRef = self.VoidPtr
        self.ThreadSafeContextRef = self.VoidPtr
        self.LLJITBuilderRef = self.VoidPtr
        self.LLJITRef = self.VoidPtr
        self.LLJITRefPtr = self.VoidPtrPtr
        self.ErrorRef = self.VoidPtr
        self.ExecutionSessionRef = self.VoidPtr
        self.JITTargetAddress = self.VoidPtr
        self.PassManagerRef = self.VoidPtrPtr
        self.JITTargetMachineBuilderRef = self.VoidPtr
        self.TargetMachineRef = self.VoidPtr
        self.TargetRef = self.VoidPtr
        self.PassManagerRef = self.VoidPtr
        self.PassManagerBuilderRef = self.VoidPtr
        self.MetadataRef = self.VoidPtr
        self.MetadataRefPtr = self.VoidPtrPtr
        self.ExecutionSessionRef = self.VoidPtr
        self.ObjectLayerRef = self.VoidPtr
        self.AttributeRef = self.VoidPtr
        self.MemoryManagerFactoryFunction = self.VoidPtr
        self.ObjectLinkingLayerCreatorFunction = self.VoidPtr
        self.DefinitionGeneratorRef = self.VoidPtr
        self.DefinitionGeneratorRefPtr = self.VoidPtrPtr
        self.ResourceTrackerRef = self.VoidPtr
        self.JITEnums = lltype.Struct('JITEnums', ('codegenlevel', lltype.Signed), ('reloc', lltype.Signed), ('codemodel', lltype.Signed))
        self.CmpEnums = lltype.Struct('CmpEnums', ('inteq', lltype.Signed), ('intne', lltype.Signed), ('intugt', lltype.Signed), ('intuge', lltype.Signed), ('intult', lltype.Signed), ('intule', lltype.Signed), ('intsgt', lltype.Signed), ('intsge', lltype.Signed), ('intslt', lltype.Signed), ('intsle', lltype.Signed), ('realeq', lltype.Signed), ('realne', lltype.Signed), ('realgt', lltype.Signed), ('realge', lltype.Signed), ('reallt', lltype.Signed), ('realle', lltype.Signed),('realord', lltype.Signed), ('uno', lltype.Signed))

    def initialise_api(self):
        header_files = ["Core","Target","Analysis","DataTypes",
                        "Error","ErrorHandling","ExternC",
                        "Initialization","Orc","TargetMachine","Types",
                        "LLJIT","OrcEE"]
        header_files += ["Transforms/"+f for f in ("AggressiveInstCombine",
                                                   "IPO", "InstCombine",
                                                   "PassManagerBuilder",
                                                   "Scalar", "Utils",
                                                   "Vectorize")]
        llvm_c = ["llvm-c/"+f+".h" for f in header_files]
        cflags = [os.popen("llvm-config --cflags").read().strip()]
        ldflags = os.popen("llvm-config --ldflags").read().strip()[2:]
        libs = [lib[2:] for lib in os.popen("llvm-config --libs all")
                .read().strip().split()]
        libs.append("wrapper")
        include_dir = cflags[0].split()[0][2:]
        path = pypydir+"/../rpython/jit/backend/llvm/llvm_wrapper/"
        path2 = pypydir+"/../rpython/jit/backend/llvm/" #wrapper libs need to be in the same directory as the python file, don't ask why

        info = ExternalCompilationInfo(includes=llvm_c+[path2+"wrapper.h"],
                                       libraries=libs,
                                       include_dirs=[ldflags, include_dir,
                                                     path, path2],
                                       library_dirs=[ldflags, path, path2],
                                       compile_extra=cflags, link_extra=cflags)

        self.CreateModule = rffi.llexternal("LLVMModuleCreateWithNameInContext",
                                            [self.Str, self.ContextRef], self.ModuleRef,
                                            compilation_info=info)
        self.FunctionType = rffi.llexternal("LLVMFunctionType",
                                            [self.TypeRef, self.TypeRefPtr,
                                             lltype.Unsigned, self.Bool],
                                            self.TypeRef, compilation_info=info)
        self.AddFunction = rffi.llexternal("LLVMAddFunction",
                                           [self.ModuleRef, self.Str, self.TypeRef],
                                           self.ValueRef, compilation_info=info)
        self.AppendBasicBlock = rffi.llexternal("LLVMAppendBasicBlockInContext",
                                                [self.ContextRef, self.ValueRef, self.Str],
                                                self.BasicBlockRef,
                                                compilation_info=info)
        self.CreateBuilder = rffi.llexternal("LLVMCreateBuilderInContext",
                                             [self.ContextRef], self.BuilderRef,
                                             compilation_info=info)
        self.PositionBuilderAtEnd = rffi.llexternal("LLVMPositionBuilderAtEnd",
                                                    [self.BuilderRef,
                                                     self.BasicBlockRef], self.Void,
                                                    compilation_info=info)
        self.BuildAdd = rffi.llexternal("LLVMBuildAdd",
                                        [self.BuilderRef, self.ValueRef,
                                         self.ValueRef, self.Str],
                                        self.ValueRef, compilation_info=info)
        self.BuildFAdd = rffi.llexternal("LLVMBuildAdd",
                                         [self.BuilderRef, self.ValueRef,
                                          self.ValueRef, self.Str],
                                         self.ValueRef, compilation_info=info)
        self.BuildRet = rffi.llexternal("LLVMBuildRet",
                                        [self.BuilderRef, self.ValueRef],
                                        self.ValueRef, compilation_info=info)
        self.GetInsertBlock = rffi.llexternal("LLVMGetInsertBlock",
                                        [self.BuilderRef],
                                        self.BasicBlockRef, compilation_info=info)
        self.GetParam = rffi.llexternal("LLVMGetParam",
                                        [self.ValueRef, lltype.Signed],
                                        self.ValueRef, compilation_info=info)
        self.VerifyModule = rffi.llexternal("VerifyModule",
                                            [self.ModuleRef],
                                            self.Bool,
                                            compilation_info=info)
        self.DisposeMessage = rffi.llexternal("LLVMDisposeMessage",
                                              [self.Str], self.Void,
                                              compilation_info=info)
        self.DisposeBuilder = rffi.llexternal("LLVMDisposeBuilder",
                                              [self.BuilderRef], self.Void,
                                              compilation_info=info)
        self.DisposeModule = rffi.llexternal("LLVMDisposeModule",
                                            [self.ModuleRef], self.Void,
                                            compilation_info=info)
        self.IntType = rffi.llexternal("LLVMIntTypeInContext",
                                       [self.ContextRef, lltype.Unsigned],
                                       self.TypeRef,
                                       compilation_info=info)
        self.ConstInt = rffi.llexternal("LLVMConstInt",
                                        [self.TypeRef, lltype.UnsignedLongLong,
                                         self.Bool], self.ValueRef,
                                        compilation_info=info)
        self.InitializeCore = rffi.llexternal("LLVMInitializeCore",
                                              [self.Void], self.Bool,
                                              compilation_info=info)
        self.BuildPhi = rffi.llexternal("LLVMBuildPhi",
                                        [self.BuilderRef, self.TypeRef, self.Str],
                                        self.ValueRef, compilation_info=info)
        self.GetInsertBlock = rffi.llexternal("LLVMGetInsertBlock",
                                              [self.BuilderRef], self.BasicBlockRef,
                                              compilation_info=info)
        self.PositionBuilderAtEnd = rffi.llexternal("LLVMPositionBuilderAtEnd",
                                                    [self.BuilderRef,
                                                     self.BasicBlockRef],
                                                    self.Void, compilation_info=info)
        self.BuildFCmp = rffi.llexternal("LLVMBuildFCmp",
                                         [self.BuilderRef, self.RealPredicate,
                                          self.ValueRef, self.ValueRef,
                                          self.Str], self.ValueRef,
                                          compilation_info=info)
        self.BuildICmp = rffi.llexternal("LLVMBuildICmp",
                                         [self.BuilderRef, lltype.Signed,
                                          self.ValueRef, self.ValueRef,
                                          self.Str], self.ValueRef,
                                         compilation_info=info)
        self.CreateBasicBlock = rffi.llexternal("LLVMCreateBasicBlockInContext",
                                                [self.ContextRef, self.Str],
                                                self.BasicBlockRef,
                                                compilation_info=info)
        self.GetParent = rffi.llexternal("LLVMGetBasicBlockParent",
                                         [self.BasicBlockRef], self.ValueRef,
                                         compilation_info=info)
        self.AddIncoming = rffi.llexternal("AddIncoming",
                                           [self.ValueRef, self.ValueRef,
                                            self.BasicBlockRef],
                                           self.Void, compilation_info=info)
        self.BuildBr = rffi.llexternal("LLVMBuildBr",
                                       [self.BuilderRef, self.BasicBlockRef],
                                       self.ValueRef, compilation_info=info)
        self.BuildCondBr = rffi.llexternal("LLVMBuildCondBr",
                                           [self.BuilderRef, self.ValueRef,
                                            self.BasicBlockRef, self.BasicBlockRef],
                                           self.ValueRef, compilation_info=info)
        self.GetDataLayout = rffi.llexternal("LLVMGetDataLayoutStr",
                                             [self.ModuleRef], self.Str,
                                             compilation_info=info)
        self.SetModuleDataLayout = rffi.llexternal("LLVMSetModuleDataLayout",
                                                   [self.ModuleRef,
                                                    self.TargetDataRef],
                                                   self.Void, compilation_info=info)
        self.CreateTargetData = rffi.llexternal("LLVMCreateTargetData",
                                                [self.Str], self.TargetDataRef,
                                                compilation_info=info)
        self.InitializeNativeTarget = rffi.llexternal("InitializeNativeTarget",
                                                      [self.Void], self.Bool,
                                                      compilation_info=info)
        self.InitializeNativeAsmPrinter = rffi.llexternal("InitializeNativeAsmPrinter",
                                                          [self.Void], self.Bool,
                                                          compilation_info=info)
        self.CreateThreadSafeModule = rffi.llexternal("LLVMOrcCreateNewThreadSafeModule",
                                                         [self.ModuleRef,
                                                          self.ThreadSafeContextRef],
                                                        self.ThreadSafeModuleRef,
                                                         compilation_info=info)
        self.CreateThreadSafeContext = rffi.llexternal("LLVMOrcCreateNewThreadSafeContext",
                                                         [self.Void],
                                                       self.ThreadSafeContextRef,
                                                         compilation_info=info)
        self.GetContext = rffi.llexternal("LLVMOrcThreadSafeContextGetContext",
                                          [self.ThreadSafeContextRef],
                                          self.ContextRef,
                                          compilation_info=info)
        self.LLJITLookup = rffi.llexternal("LLJITLookup",
                                           [self.LLJITRef,
                                            self.Str], self.JITTargetAddress,
                                           compilation_info=info)
        self.LLJITAddModule = rffi.llexternal("LLVMOrcLLJITAddLLVMIRModuleWithRT",
                                              [self.LLJITRef,
                                               self.ResourceTrackerRef,
                                               self.ThreadSafeModuleRef],
                                              self.ErrorRef,
                                              compilation_info=info)
        self.LLJITGetMainJITDylib = rffi.llexternal("LLVMOrcLLJITGetMainJITDylib",
                                                    [self.LLJITRef],
                                                    self.JITDylibRef,
                                                    compilation_info=info)
        self.LLJITGetExecutionSession = rffi.llexternal("LLVMOrcExecutionSessionRef",
                                                        [self.LLJITRef],
                                                        self.ExecutionSessionRef,
                                                        compilation_info=info)
        self.CreateLLJIT = rffi.llexternal("CreateLLJIT",
                                           [self.LLJITBuilderRef],
                                           self.LLJITRef,
                                           compilation_info=info)
        self.CreateLLJITBuilder = rffi.llexternal("LLVMOrcCreateLLJITBuilder",
                                                         [self.Void],
                                                        self.LLJITBuilderRef,
                                                         compilation_info=info)
        self.CreatePassManager = rffi.llexternal("LLVMCreatePassManager",
                                                 [self.Void],
                                                 self.PassManagerRef,
                                                 compilation_info=info)
        self.RunPassManager = rffi.llexternal("LLVMRunPassManager",
                                              [self.PassManagerRef,
                                               self.ModuleRef], self.Bool,
                                              compilation_info=info)
        self.LLJITBuilderSetJITTargetMachineBuilder = rffi.llexternal("LLVMOrcLLJITBuilderSetJITTargetMachineBuilder",
                                                                      [self.LLJITBuilderRef,
                                                                       self.JITTargetMachineBuilderRef],
                                                                      self.Void,
                                                                      compilation_info=info)
        self.JITTargetMachineBuilderCreateFromTargetMachine = rffi.llexternal("LLVMOrcJITTargetMachineBuilderCreateFromTargetMachine",
                                                                              [self.TargetMachineRef],
                                                                              self.JITTargetMachineBuilderRef,
                                                                              compilation_info=info)
        self.GetHostCPUName = rffi.llexternal("LLVMGetHostCPUName",
                                              [self.Void],
                                              self.Str,
                                              compilation_info=info)
        self.GetHostCPUFeatures = rffi.llexternal("LLVMGetHostCPUFeatures",
                                                  [self.Void],
                                                  self.Str,
                                                  compilation_info=info)
        self.GetHostCPUFeatures = rffi.llexternal("LLVMGetHostCPUFeatures",
                                                  [self.Void],
                                                  self.Str,
                                                  compilation_info=info)
        self.CreateTargetMachine = rffi.llexternal("LLVMCreateTargetMachine",
                                                   [self.TargetRef,
                                                    self.Str, self.Str,
                                                    self.Str, self.Enum,
                                                    self.Enum, self.Enum],
                                                   self.TargetMachineRef,
                                                   compilation_info=info)
        self.GetTarget = rffi.llexternal("GetTargetFromTriple",
                                         [self.Str],
                                         self.TargetRef,
                                         compilation_info=info)
        self.CreateTargetDataLayout = rffi.llexternal("LLVMCreateTargetDataLayout",
                                                      [self.TargetMachineRef],
                                                      self.TargetDataRef,
                                                      compilation_info=info)
        self.GetTargetTriple = rffi.llexternal("LLVMGetDefaultTargetTriple",
                                               [self.Void],
                                               self.Str,
                                               compilation_info=info)
        self.GetParam = rffi.llexternal("LLVMGetParam",
                                         [self.ValueRef, lltype.Signed],
                                         self.ValueRef,
                                         compilation_info=info)
        self.PositionBuilderBefore = rffi.llexternal("LLVMPositionBuilderBefore",
                                                      [self.BuilderRef,
                                                       self.BasicBlockRef],
                                                      self.Void,
                                                      compilation_info=info)
        self.EraseInstruction = rffi.llexternal("LLVMInstructionEraseFromParent",
                                                 [self.ValueRef],
                                                 self.Void,
                                                 compilation_info=info)
        self.GetFirstInstruction = rffi.llexternal("LLVMGetFirstInstruction",
                                                    [self.BasicBlockRef],
                                                    self.ValueRef,
                                                    compilation_info=info)
        self.CloneModule = rffi.llexternal("LLVMCloneModule",
                                            [self.ModuleRef],
                                            self.ModuleRef,
                                            compilation_info=info)
        self.TypeOf = rffi.llexternal("LLVMTypeOf",
                                       [self.ValueRef],
                                       self.TypeRef,
                                       compilation_info=info)
        self.VoidType = rffi.llexternal("LLVMVoidTypeInContext",
                                         [self.ContextRef],
                                         self.TypeRef,
                                         compilation_info=info)
        self.StructType = rffi.llexternal("LLVMStructTypeInContext",
                                           [self.ContextRef, self.TypeRefPtr,
                                            lltype.Unsigned, self.Bool],
                                           self.TypeRef,
                                           compilation_info=info)
        self.ArrayType = rffi.llexternal("LLVMArrayType",
                                          [self.TypeRef, lltype.Unsigned],
                                          self.TypeRef,
                                          compilation_info=info)
        self.PointerType = rffi.llexternal("LLVMPointerType",
                                            [self.TypeRef, lltype.Unsigned],
                                            self.TypeRef,
                                            compilation_info=info)
        self.BuildStructGEP = rffi.llexternal("LLVMBuildStructGEP2",
                                               [self.BuilderRef, self.TypeRef,
                                                self.ValueRef, lltype.Unsigned,
                                                self.Str],
                                               self.ValueRef,
                                               compilation_info=info)
        self.BuildGEP = rffi.llexternal("LLVMBuildInBoundsGEP2",
                                        [self.BuilderRef, self.TypeRef,
                                         self.ValueRef, self.ValueRefPtr,
                                         lltype.Unsigned, self.Str],
                                        self.ValueRef,
                                        compilation_info=info)
        self.BuildLoad = rffi.llexternal("LLVMBuildLoad2",
                                          [self.BuilderRef, self.TypeRef,
                                           self.ValueRef, self.Str],
                                          self.ValueRef,
                                          compilation_info=info)
        self.BuildStore = rffi.llexternal("LLVMBuildStore",
                                           [self.BuilderRef, self.ValueRef,
                                            self.ValueRef],
                                           self.ValueRef,
                                           compilation_info=info)
        self.BuildBitCast = rffi.llexternal("LLVMBuildBitCast",
                                             [self.BuilderRef, self.ValueRef,
                                              self.TypeRef, self.Str],
                                             self.ValueRef,
                                             compilation_info=info)
        self.BuildIntToPtr = rffi.llexternal("LLVMBuildIntToPtr",
                                              [self.BuilderRef, self.ValueRef,
                                               self.TypeRef, self.Str],
                                              self.ValueRef,
                                              compilation_info=info)
        self.BuildPtrToInt = rffi.llexternal("LLVMBuildPtrToInt",
                                              [self.BuilderRef, self.ValueRef,
                                               self.TypeRef, self.Str],
                                              self.ValueRef,
                                              compilation_info=info)
        self.WriteBitcodeToFile = rffi.llexternal("LLVMWriteBitcodeToFile",
                                                   [self.ModuleRef, self.Str],
                                                   self.ValueRef,
                                                   compilation_info=info)
        self.BuildAlloca = rffi.llexternal("LLVMBuildAlloca",
                                            [self.BuilderRef, self.TypeRef,
                                             self.Str],
                                            self.ValueRef,
                                            compilation_info=info)
        self.PositionBuilderBefore = rffi.llexternal("LLVMPositionBuilderBefore",
                                                      [self.BuilderRef, self.ValueRef],
                                                      self.Void,
                                                      compilation_info=info)
        self.GetFirstInstruction = rffi.llexternal("LLVMGetFirstInstruction",
                                                    [self.BasicBlockRef],
                                                    self.ValueRef,
                                                    compilation_info=info)
        self.BuildMemCpy = rffi.llexternal("LLVMBuildMemCpy",
                                            [self.BuilderRef, self.ValueRef,
                                             lltype.Unsigned, self.ValueRef,
                                             lltype.Unsigned, self.ValueRef],
                                            self.ValueRef,
                                            compilation_info=info)
        self.CreatePassManager = rffi.llexternal("LLVMCreatePassManager",
                                                  [self.Void],
                                                  self.PassManagerRef,
                                                  compilation_info=info)
        self.RunPassManager = rffi.llexternal("LLVMRunPassManager",
                                               [self.PassManagerRef,
                                                self.ModuleRef],
                                               self.Bool,
                                               compilation_info=info)
        self.AddInstructionCombiningPass = rffi.llexternal("LLVMAddInstructionCombiningPass",
                                                            [self.PassManagerRef],
                                                            self.Void,
                                                            compilation_info=info)
        self.AddReassociatePass = rffi.llexternal("LLVMAddReassociatePass",
                                                   [self.PassManagerRef],
                                                   self.Void,
                                                   compilation_info=info)
        self.AddGVNPass = rffi.llexternal("LLVMAddNewGVNPass",
                                           [self.PassManagerRef],
                                           self.Void,
                                           compilation_info=info)
        self.AddCFGSimplificationPass = rffi.llexternal("LLVMAddCFGSimplificationPass",
                                           [self.PassManagerRef],
                                           self.Void,
                                           compilation_info=info)
        self.AddPromoteMemoryToRegisterPass = rffi.llexternal("LLVMAddPromoteMemoryToRegisterPass",
                                                               [self.PassManagerRef],
                                                               self.Void,
                                                               compilation_info=info)
        self.AddPromoteMemoryToRegisterPass = rffi.llexternal("LLVMAddPromoteMemoryToRegisterPass",
                                                               [self.PassManagerRef],
                                                               self.Void,
                                                               compilation_info=info)
        self.AddIndVarSimplifyPass = rffi.llexternal("LLVMAddIndVarSimplifyPass",
                                                      [self.PassManagerRef],
                                                      self.Void,
                                                      compilation_info=info)
        self.AddScalarReplAggregatesPass = rffi.llexternal("LLVMAddScalarReplAggregatesPass",
                                                            [self.PassManagerRef],
                                                            self.Void,
                                                            compilation_info=info)
        self.AddScalarReplAggregatesPass = rffi.llexternal("LLVMAddScalarReplAggregatesPass",
                                                            [self.PassManagerRef],
                                                            self.Void,
                                                            compilation_info=info)
        self.GetSubtypes = rffi.llexternal("LLVMGetSubtypes",
                                            [self.TypeRef, self.TypeRefPtr],
                                            self.Void,
                                            compilation_info=info)
        self.DeleteBasicBlock = rffi.llexternal("LLVMDeleteBasicBlock",
                                                 [self.BasicBlockRef],
                                                 self.Void,
                                                 compilation_info=info)
        self.BuildZExt = rffi.llexternal("LLVMBuildZExt",
                                          [self.BuilderRef, self.ValueRef,
                                           self.TypeRef, self.Str],
                                          self.ValueRef,
                                          compilation_info=info)
        self.SizeOf = rffi.llexternal("GetSizeOf",
                                       [self.TypeRef],
                                       lltype.SignedLongLong,
                                       compilation_info=info)
        self.DeleteBasicBlock = rffi.llexternal("LLVMDeleteBasicBlock",
                                       [self.BasicBlockRef],
                                       lltype.Void,
                                       compilation_info=info)
        self.DisposeLLJIT = rffi.llexternal("LLVMOrcDisposeLLJIT",
                                       [self.LLJITRef],
                                       self.ErrorRef,
                                       compilation_info=info)
        self.GetErrorMessage = rffi.llexternal("LLVMGetErrorMessage",
                                                [self.ErrorRef],
                                                self.Str,
                                                compilation_info=info)
        self.FloatType = rffi.llexternal("LLVMDoubleTypeInContext",
                                          [self.ContextRef],
                                          self.TypeRef,
                                          compilation_info=info)
        self.SingleFloatType = rffi.llexternal("LLVMFloatTypeInContext",
                                               [self.ContextRef],
                                               self.TypeRef,
                                               compilation_info=info)
        self.ConstFloat = rffi.llexternal("LLVMConstReal",
                                          [self.TypeRef, lltype.Float],
                                          self.ValueRef,
                                          compilation_info=info)
        self.BuildFAdd = rffi.llexternal("LLVMBuildFAdd",
                                          [self.BuilderRef, self.ValueRef,
                                           self.ValueRef, self.Str],
                                          self.ValueRef,
                                          compilation_info=info)
        self.PrintValue = rffi.llexternal("LLVMPrintValueToString",
                                           [self.ValueRef],
                                           self.Str,
                                           compilation_info=info)
        self.BuildSub = rffi.llexternal("LLVMBuildSub",
                                         [self.BuilderRef, self.ValueRef,
                                          self.ValueRef, self.Str],
                                         self.ValueRef,
                                         compilation_info=info)
        self.BuildFSub = rffi.llexternal("LLVMBuildFSub",
                                          [self.BuilderRef, self.ValueRef,
                                           self.ValueRef, self.Str],
                                          self.ValueRef,
                                          compilation_info=info)
        self.BuildMul = rffi.llexternal("LLVMBuildMul",
                                         [self.BuilderRef, self.ValueRef,
                                          self.ValueRef, self.Str],
                                         self.ValueRef,
                                         compilation_info=info)
        self.BuildFMul = rffi.llexternal("LLVMBuildFMul",
                                          [self.BuilderRef, self.ValueRef,
                                           self.ValueRef, self.Str],
                                          self.ValueRef,
                                          compilation_info=info)
        self.BuildFMul = rffi.llexternal("LLVMBuildFMul",
                                          [self.BuilderRef, self.ValueRef,
                                           self.ValueRef, self.Str],
                                          self.ValueRef,
                                          compilation_info=info)
        self.BuildFDiv = rffi.llexternal("LLVMBuildFDiv",
                                          [self.BuilderRef, self.ValueRef,
                                           self.ValueRef, self.Str],
                                          self.ValueRef,
                                          compilation_info=info)
        self.BuildUDiv = rffi.llexternal("LLVMBuildUDiv",
                                          [self.BuilderRef, self.ValueRef,
                                           self.ValueRef, self.Str],
                                          self.ValueRef,
                                          compilation_info=info)
        self.BuildAnd = rffi.llexternal("LLVMBuildAnd",
                                         [self.BuilderRef, self.ValueRef,
                                          self.ValueRef, self.Str],
                                         self.ValueRef,
                                         compilation_info=info)
        self.BuildOr = rffi.llexternal("LLVMBuildOr",
                                        [self.BuilderRef, self.ValueRef,
                                         self.ValueRef, self.Str],
                                        self.ValueRef,
                                        compilation_info=info)
        self.BuildXor = rffi.llexternal("LLVMBuildXor",
                                         [self.BuilderRef, self.ValueRef,
                                          self.ValueRef, self.Str],
                                         self.ValueRef,
                                         compilation_info=info)
        self.BuildFNeg = rffi.llexternal("LLVMBuildFNeg",
                                          [self.BuilderRef, self.ValueRef,
                                           self.Str],
                                          self.ValueRef,
                                          compilation_info=info)
        self.BuildLShl = rffi.llexternal("LLVMBuildShl",
                                          [self.BuilderRef, self.ValueRef,
                                           self.ValueRef, self.Str],
                                          self.ValueRef,
                                          compilation_info=info)
        self.BuildURShl = rffi.llexternal("LLVMBuildLShr",
                                           [self.BuilderRef, self.ValueRef,
                                            self.ValueRef, self.Str],
                                           self.ValueRef,
                                           compilation_info=info)
        self.BuildRShl = rffi.llexternal("LLVMBuildAShr",
                                          [self.BuilderRef, self.ValueRef,
                                           self.ValueRef, self.Str],
                                          self.ValueRef,
                                          compilation_info=info)
        self.BuildSExt = rffi.llexternal("LLVMBuildSExt",
                                          [self.BuilderRef, self.ValueRef,
                                           self.TypeRef, self.Str],
                                          self.ValueRef,
                                          compilation_info=info)
        self.SetJITEnums = rffi.llexternal("SetJITEnums",
                                            [lltype.Ptr(self.JITEnums)],
                                            self.Void,
                                            compilation_info=info)
        self.SetCmpEnums = rffi.llexternal("SetCmpEnums",
                                            [lltype.Ptr(self.CmpEnums)],
                                            self.Void,
                                            compilation_info=info)
        self.getResultElementType = rffi.llexternal("getResultElementType",
                                                     [self.ValueRef],
                                                     self.TypeRef,
                                                     compilation_info=info)
        self.DumpValue = rffi.llexternal("LLVMDumpValue",
                                         [self.ValueRef],
                                         self.Void,
                                         compilation_info=info)
        self.removeIncomingValue = rffi.llexternal("removeIncomingValue",
                                                   [self.ValueRef,
                                                    self.BasicBlockRef],
                                                   self.ValueRef,
                                                   compilation_info=info)
        self.removePredecessor = rffi.llexternal("removePredecessor",
                                                 [self.BasicBlockRef,
                                                  self.BasicBlockRef],
                                                 self.Void,
                                                 compilation_info=info)
        self.getFirstNonPhi = rffi.llexternal("getFirstNonPhi",
                                              [self.BasicBlockRef],
                                              self.Void,
                                              compilation_info=info)
        self.splitBasicBlockAtPhi = rffi.llexternal("splitBasicBlockAtPhi",
                                               [self.BasicBlockRef],
                                               self.BasicBlockRef,
                                               compilation_info=info)
        self.getTerminator = rffi.llexternal("getTerminator",
                                             [self.BasicBlockRef],
                                             self.ValueRef,
                                             compilation_info=info)
        self.DumpModule = rffi.llexternal("LLVMDumpModule",
                                          [self.ModuleRef],
                                          self.Void,
                                          compilation_info=info)
        self.dumpBasicBlock = rffi.llexternal("dumpBasicBlock",
                                              [self.ModuleRef],
                                              self.Void,
                                              compilation_info=info)
        self.getIncomingValueForBlock = rffi.llexternal("getIncomingValueForBlock",
                                                        [self.ValueRef,
                                                         self.BasicBlockRef],
                                                        self.ValueRef,
                                                        compilation_info=info)
        self.GetLastInstruction = rffi.llexternal("LLVMGetLastInstruction",
                                                  [self.BasicBlockRef],
                                                  self.ValueRef,
                                                  compilation_info=info)
        self.BuildPtrDiff = rffi.llexternal("LLVMBuildPtrDiff",
                                            [self.BuilderRef, self.ValueRef,
                                             self.ValueRef, self.Str],
                                            self.ValueRef,
                                            compilation_info=info)
        self.BuildFNeg = rffi.llexternal("LLVMBuildFNeg",
                                         [self.BuilderRef, self.ValueRef,
                                          self.Str],
                                         self.ValueRef,
                                         compilation_info=info)
        self.BuildSelect = rffi.llexternal("LLVMBuildSelect",
                                           [self.BuilderRef, self.ValueRef,
                                            self.ValueRef, self.ValueRef,
                                            self.Str],
                                           self.ValueRef,
                                           compilation_info=info)
        self.MDString = rffi.llexternal("LLVMMDStringInContext2",
                                        [self.ContextRef, self.Str,
                                         lltype.Unsigned],
                                        self.MetadataRef,
                                        compilation_info=info)
        self.MetadataAsValue = rffi.llexternal("LLVMMetadataAsValue",
                                               [self.ContextRef,
                                                self.MetadataRef],
                                               self.ValueRef,
                                               compilation_info=info)
        self.GetMDKindID = rffi.llexternal("LLVMGetMDKindIDInContext",
                                           [self.ContextRef, self.Str,
                                            lltype.Unsigned],
                                           lltype.Unsigned,
                                           compilation_info=info)
        self.SetMetadata = rffi.llexternal("LLVMSetMetadata",
                                           [self.ValueRef, lltype.Unsigned,
                                            self.ValueRef],
                                           self.Void,
                                           compilation_info=info)
        self.BuildNeg = rffi.llexternal("LLVMBuildNeg",
                                        [self.BuilderRef, self.ValueRef,
                                         self.Str],
                                        self.ValueRef,
                                        compilation_info=info)
        self.BuildNSWMul = rffi.llexternal("LLVMBuildNSWMul",
                                           [self.BuilderRef, self.ValueRef,
                                            self.ValueRef, self.Str],
                                           self.ValueRef,
                                           compilation_info=info)
        self.BuildNUWMul = rffi.llexternal("LLVMBuildNUWMul",
                                           [self.BuilderRef, self.ValueRef,
                                            self.ValueRef, self.Str],
                                           self.ValueRef,
                                           compilation_info=info)
        self.BuildIsNull = rffi.llexternal("LLVMBuildIsNull",
                                           [self.BuilderRef, self.ValueRef,
                                            self.Str],
                                           self.ValueRef,
                                           compilation_info=info)
        self.BuildIsNotNull = rffi.llexternal("LLVMBuildIsNotNull",
                                              [self.BuilderRef, self.ValueRef,
                                               self.Str],
                                              self.ValueRef,
                                              compilation_info=info)
        self.BuildNeg = rffi.llexternal("LLVMBuildNeg",
                                        [self.BuilderRef, self.ValueRef,
                                         self.Str],
                                        self.ValueRef,
                                        compilation_info=info)
        self.BuildTrunc = rffi.llexternal("LLVMBuildTrunc",
                                          [self.BuilderRef, self.ValueRef,
                                           self.TypeRef, self.Str],
                                          self.ValueRef,
                                          compilation_info=info)
        self.BuildCall = rffi.llexternal("LLVMBuildCall",
                                         [self.BuilderRef, self.ValueRef,
                                          self.ValueRefPtr, lltype.Unsigned,
                                          self.Str],
                                         self.ValueRef,
                                         compilation_info=info)
        self.VoidType = rffi.llexternal("LLVMVoidTypeInContext",
                                        [self.ContextRef],
                                        self.TypeRef,
                                        compilation_info=info)
        self.GetExecutionSession = rffi.llexternal("LLVMOrcLLJITGetExecutionSession",
                                        [self.LLJITRef],
                                        self.ExecutionSessionRef,
                                        compilation_info=info)
        self.BuildIntCast = rffi.llexternal("LLVMBuildIntCast2",
                                            [self.BuilderRef, self.ValueRef,
                                             self.TypeRef, self.Bool,
                                             self.Str],
                                            self.ValueRef,
                                            compilation_info=info)
        self.BuildPointerCast = rffi.llexternal("LLVMBuildPointerCast",
                                                [self.BuilderRef, self.ValueRef,
                                                 self.TypeRef, self.Str],
                                                self.ValueRef,
                                                compilation_info=info)
        self.CreateObjectLinkingLayer = rffi.llexternal(
            "LLVMOrcCreateRTDyldObjectLinkingLayer",
            [self.ExecutionSessionRef, self.MemoryManagerFactoryFunction,
             self.VoidPtr],
            self.ObjectLayerRef,
            compilation_info=info)
        self.SetObjectLinkingLayerCreator = rffi.llexternal(
            "LLVMOrcLLJITBuilderSetObjectLinkingLayerCreator",
            [self.LLJITBuilderRef, self.ObjectLinkingLayerCreatorFunction,
             self.VoidPtr], self.Void, compilation_info=info)
        self.AppendInlineAsm = rffi.llexternal("LLVMAppendModuleInlineAsm",
                                               [self.ModuleRef, self.Str,
                                                lltype.Unsigned],
                                               self.Void,
                                               compilation_info=info)
        self.ConstString = rffi.llexternal("LLVMConstStringInContext",
                                           [self.ContextRef, self.Str,
                                            lltype.Unsigned, self.Bool],
                                           self.ValueRef,
                                           compilation_info=info)
        self.create_breakpoint = rffi.llexternal("create_breakpoint", [],
                                                 self.Void,
                                                 compilation_info=info)
        self.ValueAsMetadata = rffi.llexternal("LLVMValueAsMetadata",
                                               [self.ValueRef],
                                               self.MetadataRef,
                                               compilation_info=info)
        self.MDNode = rffi.llexternal("LLVMMDNodeInContext2",
                                      [self.ContextRef, self.MetadataRefPtr,
                                       lltype.Unsigned],
                                      self.MetadataRef,
                                      compilation_info=info)
        self.SetTarget = rffi.llexternal("LLVMSetTarget",
                                         [self.ModuleRef, self.Str],
                                         self.Void, compilation_info=info)
        self.PrintTypeToString = rffi.llexternal("LLVMPrintTypeToString",
                                                 [self.TypeRef],
                                                 self.Str,
                                                 compilation_info=info)
        self.DumpType = rffi.llexternal("LLVMDumpType",
                                        [self.TypeRef],
                                        self.Void,
                                        compilation_info=info)
        self.FloatTrunc = rffi.llexternal("LLVMBuildFPTrunc",
                                          [self.BuilderRef, self.ValueRef,
                                           self.TypeRef, self.Str],
                                          self.Str,
                                          compilation_info=info)
        self.FloatExt = rffi.llexternal("LLVMBuildFPExt",
                                        [self.BuilderRef, self.ValueRef,
                                         self.TypeRef, self.Str],
                                        self.Str,
                                        compilation_info=info)
        self.add_function_attribute = rffi.llexternal("add_function_attribute",
                                                      [self.ValueRef, self.Str,
                                                       lltype.Unsigned,
                                                       self.ContextRef],
                                                      self.Void,
                                                      compilation_info=info)
        self.add_param_attribute = rffi.llexternal("add_param_attribute",
                                                   [self.ValueRef, self.Str,
                                                    lltype.Unsigned, self.ContextRef,
                                                    lltype.Unsigned], self.Void,
                                                   compilation_info=info)
        self.AddCallSiteAttribute = rffi.llexternal("LLVMAddCallSiteAttribute",
                                                    [self.ValueRef, lltype.Signed,
                                                    self.AttributeRef], self.Void,
                                                   compilation_info=info)
        self.SetTailCall = rffi.llexternal("LLVMSetTailCall",
                                           [self.ValueRef, self.Bool],
                                           self.Void,
                                           compilation_info=info)
        self.add_function_string_attribute = rffi.llexternal("add_function_string_attribute",
                                                             [self.ValueRef, self.Str,
                                                              self.Str, self.ContextRef],
                                                             self.Void,
                                                             compilation_info=info)
        self.BuildFPToSI = rffi.llexternal("LLVMBuildFPToSI",
                                           [self.BuilderRef, self.ValueRef,
                                            self.TypeRef, self.Str],
                                           self.ValueRef,
                                           compilation_info=info)
        self.BuildFPToUI = rffi.llexternal("LLVMBuildFPToUI",
                                           [self.BuilderRef, self.ValueRef,
                                            self.TypeRef, self.Str],
                                           self.ValueRef,
                                           compilation_info=info)
        self.BuildSIToFP = rffi.llexternal("LLVMBuildSIToFP",
                                           [self.BuilderRef, self.ValueRef,
                                            self.TypeRef, self.Str],
                                           self.ValueRef,
                                           compilation_info=info)
        self.BuildUIToFP = rffi.llexternal("LLVMBuildUIToFP",
                                           [self.BuilderRef, self.ValueRef,
                                            self.TypeRef, self.Str],
                                           self.ValueRef,
                                           compilation_info=info)
        self.AddAggressiveInstCombinerPass = rffi.llexternal("LLVMAddAggressiveInstCombinerPass",
                                                             [self.PassManagerRef],
                                                             self.Void,
                                                             compilation_info=info)
        self.AddInstructionCombiningPass = rffi.llexternal("LLVMAddInstructionCombiningPass",
                                                           [self.PassManagerRef],
                                                           self.Void,
                                                           compilation_info=info)
        self.AddLoopVectorizePass = rffi.llexternal("LLVMAddLoopVectorizePass",
                                                    [self.PassManagerRef],
                                                    self.Void,
                                                    compilation_info=info)
        self.AddSLPVectorizePass = rffi.llexternal("LLVMAddSLPVectorizePass",
                                                   [self.PassManagerRef],
                                                   self.Void,
                                                   compilation_info=info)
        self.AddScalarizerPass = rffi.llexternal("LLVMAddScalarizerPass",
                                                 [self.PassManagerRef],
                                                 self.Void,
                                                 compilation_info=info)
        self.AddMergedLoadStoreMotionPass = rffi.llexternal("LLVMAddMergedLoadStoreMotionPass",
                                                            [self.PassManagerRef],
                                                            self.Void,
                                                            compilation_info=info)
        self.AddInstructionSimplifyPass = rffi.llexternal("LLVMAddInstructionSimplifyPass",
                                                          [self.PassManagerRef],
                                                          self.Void,
                                                          compilation_info=info)
        self.AddJumpThreadingPass = rffi.llexternal("LLVMAddJumpThreadingPass",
                                                    [self.PassManagerRef],
                                                    self.Void,
                                                    compilation_info=info)
        self.AddLICMPass = rffi.llexternal("LLVMAddLICMPass",
                                           [self.PassManagerRef],
                                           self.Void,
                                           compilation_info=info)
        self.AddLoopIdiomPass = rffi.llexternal("LLVMAddLoopIdiomPass",
                                           [self.PassManagerRef],
                                           self.Void,
                                           compilation_info=info)
        self.AddLoopUnswitchPass = rffi.llexternal("LLVMAddLoopUnswitchPass",
                                                   [self.PassManagerRef],
                                                   self.Void,
                                                   compilation_info=info)
        self.AddEarlyCSEPass = rffi.llexternal("LLVMAddEarlyCSEPass",
                                               [self.PassManagerRef],
                                               self.Void,
                                               compilation_info=info)
        self.AddSCCPPass = rffi.llexternal("LLVMAddSCCPPass",
                                           [self.PassManagerRef],
                                           self.Void,
                                           compilation_info=info)
        self.AddCorrelatedValuePropagationPass = rffi.llexternal("LLVMAddCorrelatedValuePropagationPass",
                                                                 [self.PassManagerRef],
                                                                 self.Void,
                                                                 compilation_info=info)
        self.AddTypeBasedAliasAnalysisPass = rffi.llexternal("LLVMAddTypeBasedAliasAnalysisPass",
                                                             [self.PassManagerRef],
                                                             self.Void,
                                                             compilation_info=info)
        self.AddScopedNoAliasAAPass = rffi.llexternal("LLVMAddScopedNoAliasAAPass",
                                                      [self.PassManagerRef],
                                                      self.Void,
                                                      compilation_info=info)
        self.AddBasicAliasAnalysisPass = rffi.llexternal("LLVMAddBasicAliasAnalysisPass",
                                                         [self.PassManagerRef],
                                                         self.Void,
                                                         compilation_info=info)
        self.AddUnifyFunctionExitNodesPass = rffi.llexternal("LLVMAddUnifyFunctionExitNodesPass",
                                                             [self.PassManagerRef],
                                                             self.Void,
                                                             compilation_info=info)
        self.AddDCEPass = rffi.llexternal("LLVMAddDCEPass",
                                       [self.PassManagerRef],
                                       self.Void,
                                       compilation_info=info)
        self.PositionBuilder = rffi.llexternal("LLVMPositionBuilder",
                                       [self.BuilderRef, self.BasicBlockRef,
                                        self.ValueRef],
                                       self.Void,
                                       compilation_info=info)
        self.GetNextInstruction = rffi.llexternal("LLVMGetNextInstruction",
                                       [self.ValueRef],
                                       self.ValueRef,
                                       compilation_info=info)
        self.CreateResourceTracker = rffi.llexternal("LLVMOrcJITDylibCreateResourceTracker",
                                       [self.JITDylibRef],
                                       self.ResourceTrackerRef,
                                       compilation_info=info)
        self.ReleaseResourceTracker = rffi.llexternal("LLVMOrcReleaseResourceTracker",
                                       [self.ResourceTrackerRef],
                                       self.Void,
                                       compilation_info=info)
        self.ResourceTrackerRemove = rffi.llexternal("LLVMOrcResourceTrackerRemove",
                                       [self.ResourceTrackerRef],
                                       self.ErrorRef,
                                       compilation_info=info)
        self.CreateDynamicLibrarySearchGenerator = rffi.llexternal("LLVMOrcCreateDynamicLibrarySearchGeneratorForProcess",
                                       [self.DefinitionGeneratorRefPtr,
                                        rffi.CHAR, self.VoidPtr,
                                        self.VoidPtr],
                                       self.ErrorRef,
                                       compilation_info=info)
        self.JITDylibAddGenerator = rffi.llexternal("LLVMOrcJITDylibAddGenerator",
                                                    [self.JITDylibRef,
                                                     self.DefinitionGeneratorRef],
                                                    self.Void,
                                                    compilation_info=info)
        self.GetGlobalPrefix = rffi.llexternal("LLVMOrcLLJITGetGlobalPrefix",
                                               [self.LLJITRef], rffi.CHAR,
                                               compilation_info=info)
        self.AddDynamicLibrarySearchGenerator = rffi.llexternal("AddDynamicLibrarySearchGenerator",
                                                                [self.LLJITRef,
                                                                 self.JITDylibRef],
                                                                rffi.CHAR,
                                                                compilation_info=info)
        self.AddLoopRotatePass = rffi.llexternal("LLVMAddLoopRotatePass",
                                                 [self.PassManagerRef],
                                                 self.Void,
                                                 compilation_info=info)
        self.AddLoopSimplifyPass = rffi.llexternal("AddLoopSimplifyPass",
                                                   [self.PassManagerRef],
                                                   self.Void,
                                                   compilation_info=info)
        self.AddLoopStrengthReducePass = rffi.llexternal("AddLoopStrengthReducePass",
                                                         [self.PassManagerRef],
                                                         self.Void,
                                                         compilation_info=info)
        self.AddInferFunctionAttrsPass = rffi.llexternal("AddInferFunctionAttrsPass",
                                                         [self.PassManagerRef],
                                                         self.Void,
                                                         compilation_info=info)
        self.AddTargetAnalysisPasses = rffi.llexternal("AddTargetTransformationInfoPass",
                                                       [self.PassManagerRef,
                                                        self.TargetMachineRef],
                                                       self.Void,
                                                       compilation_info=info)
        self.AddTargetLibraryInfoPass = rffi.llexternal("AddTargetLibraryInfoPass",
                                                        [self.PassManagerRef,
                                                         self.Str], self.Void,
                                                        compilation_info=info)
        self.DisposePassManager = rffi.llexternal("LLVMDisposePassManager",
                                                  [self.PassManagerRef],
                                                  self.Void,
                                                  compilation_info=info)
        self.PassManagerBuilderCreate = rffi.llexternal("LLVMPassManagerBuilderCreate",
                                                        [self.Void],
                                                        self.PassManagerBuilderRef,
                                                        compilation_info=info)
        self.SetOptLevel = rffi.llexternal("LLVMPassManagerBuilderSetOptLevel",
                                           [self.PassManagerBuilderRef,
                                            lltype.Unsigned],
                                           self.Void,
                                           compilation_info=info)
        self.PopulatePassManager = rffi.llexternal("LLVMPassManagerBuilderPopulateModulePassManager",
                                                   [self.PassManagerBuilderRef,
                                                    self.PassManagerRef],
                                                   self.Void,
                                                   compilation_info=info)
        self.PassManagerBuilderDispose = rffi.llexternal("LLVMPassManagerBuilderDispose",
                                                         [self.PassManagerBuilderRef],
                                                         self.Void,
                                                         compilation_info=info)
        self.GetAttributeKindForName = rffi.llexternal("LLVMGetEnumAttributeKindForName",
                                                       [self.Str, lltype.Unsigned],
                                                       lltype.Signed,
                                                       compilation_info=info)
        self.CreateEnumAttribute = rffi.llexternal("LLVMCreateEnumAttribute",
                                                       [self.ContextRef,
                                                        lltype.Signed,
                                                        lltype.Signed],
                                                       self.AttributeRef,
                                                       compilation_info=info)
        self.add_deref_ret_attribute = rffi.llexternal("add_deref_ret_attribute",
                                                       [self.ValueRef,
                                                        lltype.Signed],
                                                       self.Void,
                                                       compilation_info=info)
        self.CountBasicBlocks = rffi.llexternal("LLVMCountBasicBlocks",
                                                [self.BasicBlockRef],
                                                lltype.Unsigned,
                                                compilation_info=info)
        self.GetBasicBlocks = rffi.llexternal("LLVMGetBasicBlocks",
                                              [self.ValueRef,
                                               self.BasicBlockRefPtr],
                                              self.Void,
                                              compilation_info=info)
        self.HasMetadata = rffi.llexternal("LLVMHasMetadata",
                                           [self.ValueRef],
                                           lltype.Signed,
                                           compilation_info=info)
        self.GetMetadata = rffi.llexternal("LLVMGetMetadata",
                                           [self.ValueRef,
                                            lltype.Unsigned],
                                           self.ValueRef,
                                           compilation_info=info)
        self.GetSuccessor = rffi.llexternal("LLVMGetSuccessor",
                                           [self.ValueRef,
                                            lltype.Unsigned],
                                           self.ValueRef,
                                           compilation_info=info)
        self.SetSuccessor = rffi.llexternal("LLVMSetSuccessor",
                                           [self.ValueRef,
                                            lltype.Unsigned,
                                            self.ValueRef],
                                           self.Void,
                                           compilation_info=info)
        self.GetMDString = rffi.llexternal("LLVMGetMDString",
                                           [self.ValueRef,
                                            lltype.Unsigned],
                                           self.Str,
                                           compilation_info=info)
        self.GetMDNodeOperands = rffi.llexternal("LLVMGetMDNodeOperands",
                                                 [self.ValueRef,
                                                  self.ValueRefPtr],
                                                 self.Void,
                                                 compilation_info=info)
        self.ConstNull = rffi.llexternal("LLVMConstNull",
                                         [self.TypeRef],
                                         self.ValueRef,
                                         compilation_info=info)

class CString:
    """
    we have to pass a cstring to nearly every llvm function, can keep
    memory usage down by having the GC free them asap
    (without ugly explicit calls to free everywhere)
    """
    def __init__(self, string):
        self.ptr = str2constcharp(string)
        self.len = len(string)
    def __del__(self):
        lltype.free(self.ptr, flavor='raw')
